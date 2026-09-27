"""CareerLens AI - FastAPI Application Server.
Provides RESTful APIs for Resume-JD Matching, Gap Analysis, Learning Roadmaps,
Interview Question Preparation, and the Interactive AI Mock Interviewer Agent.
"""

import os
import warnings
warnings.filterwarnings("ignore")

from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.sample_data import SAMPLE_RESUMES, SAMPLE_JDS
from backend.document_parser import parse_resume_document, segment_sections, extract_contact_info, clean_text
from backend.matcher import analyze_skill_gaps
from backend.llm_engine import llm_agent
from backend.mock_interviewer import create_interview_session, get_interview_session

app = FastAPI(
    title="CareerLens AI 🎯",
    description="LLM-Based Career Guidance, Resume-JD Matching & Interactive Mock Interview Agent",
    version="1.0.0"
)

# Enable CORS for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class AnalyzeTextRequest(BaseModel):
    resume_text: str
    jd_text: str
    target_role: Optional[str] = "Software Engineer"

class RoadmapRequest(BaseModel):
    missing_skills: List[Dict[str, Any]]
    target_role: Optional[str] = "Software Engineer"

class InterviewPrepRequest(BaseModel):
    resume_text: str
    jd_text: str
    matching_skills: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]

class MockStartRequest(BaseModel):
    role: str
    candidate_name: Optional[str] = "Candidate"
    questions: List[Dict[str, Any]]

class MockSubmitRequest(BaseModel):
    session_id: str
    candidate_answer: str

class BulletRewriteRequest(BaseModel):
    bullet_point: str
    target_keywords: Optional[List[str]] = []

class ProviderConfigRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareerLens AI",
        "active_provider": llm_agent.provider,
        "has_api_key": bool(llm_agent.api_key)
    }


@app.post("/api/set-provider")
def set_provider_config(config: ProviderConfigRequest):
    llm_agent.set_provider(config.provider, config.api_key)
    return {
        "status": "success",
        "provider": llm_agent.provider,
        "message": f"LLM provider updated to {llm_agent.provider}"
    }


@app.get("/api/samples")
def get_sample_data():
    return {
        "resumes": SAMPLE_RESUMES,
        "job_descriptions": SAMPLE_JDS
    }


@app.post("/api/analyze")
async def analyze_application(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_text: str = Form(...),
    target_role: Optional[str] = Form("Software Engineer")
):
    """Analyze a resume (uploaded file or pasted text) against a Job Description."""
    extracted_text = ""
    file_info = {}

    if resume_file and resume_file.filename:
        content = await resume_file.read()
        filename = resume_file.filename
        try:
            extracted_text = parse_resume_document(filename, content)
            file_info = {"filename": filename, "size_bytes": len(content)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
    elif resume_text and resume_text.strip():
        extracted_text = clean_text(resume_text)
        file_info = {"filename": "Pasted Resume Text", "size_bytes": len(resume_text.encode())}
    else:
        raise HTTPException(status_code=400, detail="Please provide a resume file or paste resume text.")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="The provided resume document contained no readable text.")

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Please provide a valid Job Description.")

    # 1. Parse contact info and sections
    contacts = extract_contact_info(extracted_text)
    sections = segment_sections(extracted_text)

    # 2. Semantic matching and skill gap calculation
    match_data = analyze_skill_gaps(extracted_text, jd_text)

    # 3. LLM Career Critique
    critique = llm_agent.generate_career_analysis(extracted_text, jd_text, match_data)

    # 4. Generate interview questions proactively
    questions = llm_agent.generate_interview_questions(extracted_text, jd_text, match_data)

    # 5. Generate learning roadmap proactively
    roadmap = llm_agent.generate_learning_roadmap(match_data["missing_skills"], target_role)

    return {
        "file_info": file_info,
        "candidate": contacts,
        "sections": {k: len(v.splitlines()) for k, v in sections.items()},
        "match_analysis": match_data,
        "career_critique": critique,
        "roadmap": roadmap,
        "interview_questions": questions,
        "target_role": target_role,
        "extracted_resume_text": extracted_text[:1200] + ("..." if len(extracted_text) > 1200 else "")
    }


@app.post("/api/roadmap")
def create_custom_roadmap(req: RoadmapRequest):
    return {
        "roadmap": llm_agent.generate_learning_roadmap(req.missing_skills, req.target_role)
    }


@app.post("/api/interview-prep")
def create_interview_bank(req: InterviewPrepRequest):
    match_data = {
        "matching_skills": req.matching_skills,
        "missing_skills": req.missing_skills
    }
    questions = llm_agent.generate_interview_questions(req.resume_text, req.jd_text, match_data)
    return {"questions": questions}


@app.post("/api/mock-interview/start")
def start_mock_interview(req: MockStartRequest):
    if not req.questions:
        raise HTTPException(status_code=400, detail="No interview questions provided.")
    session = create_interview_session(req.role, req.candidate_name or "Candidate", req.questions)
    first_q = session.get_current_question()
    return {
        "session_id": session.session_id,
        "role": session.role,
        "candidate_name": session.candidate_name,
        "current_question": first_q,
        "progress": {
            "current": 1,
            "total": len(session.questions),
            "is_finished": False
        }
    }


@app.post("/api/mock-interview/submit")
def submit_mock_answer(req: MockSubmitRequest):
    session = get_interview_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    result = session.submit_answer(req.candidate_answer)
    return result


@app.get("/api/mock-interview/report/{session_id}")
def get_mock_report(session_id: str):
    session = get_interview_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session.generate_report_card()


@app.post("/api/rewrite-bullet")
def rewrite_bullet(req: BulletRewriteRequest):
    if not req.bullet_point.strip():
        raise HTTPException(status_code=400, detail="Bullet point text is required.")
    return llm_agent.rewrite_resume_bullet(req.bullet_point, req.target_keywords or [])


# Mount static directory for frontend assets
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def serve_index():
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>CareerLens AI Frontend Loading...</h1>"
