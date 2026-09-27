# CareerLens AI 🎯
> **LLM-Based Career Guidance, Resume-JD Matching & Interactive AI Mock Interview Agent**

CareerLens AI is an intelligent placement preparation and career agent that helps students and job seekers evaluate how well their resume matches any target job description (JD), pinpoint critical skill gaps, follow an 8-week personalized learning roadmap, and practice with an interactive **AI Mock Interviewer**.

---

## 🌟 Key Features

### 1. Multi-Format Resume Ingestion
- Upload **PDF** (`pypdf`) or **DOCX** (`python-docx`) files or paste raw text.
- Automatic section segmentation: Contact Info, Education, Technical Skills, Experience, Projects, and Certifications.

### 2. Semantic Job Matching & Gap Analysis
- **500+ Skill Ontology**: Recognizes languages, frameworks, cloud tools, databases, and core CS fundamentals with fuzzy alias matching.
- **Scikit-Learn TF-IDF Cosine Similarity**: Evaluates conceptual domain relevance between your projects and the job description.
- **Categorized Skills**:
  - ✅ **Matching Skills**: Present in both resume and target JD.
  - ⚠️ **Missing / Less-Evident Skills**: Categorized into *High Priority* and *Medium Priority*.
  - 💡 **Bonus / Differentiating Skills**: Additional strengths that give you a competitive edge.
- **Dimensional Scoring**:
  - Overall Fit % (weighted hybrid score)
  - Technical Skills Match %
  - Seniority / Experience Fit %
  - Project Relevancy %
  - ATS (Applicant Tracking System) Compatibility Score & Grade

### 3. AI Recruiter Assessment & Critique
- **Executive Recruiter Summary**: Honest evaluation of candidate candidacy.
- **Core Strengths**: Highlighted selling points to emphasize in technical rounds.
- **Red Flags & Skill Deficits**: Specific vulnerabilities to address.
- **Actionable Quick Wins**: Immediate adjustments to boost candidate ranking.

### 4. 8-Week Personalized Learning Roadmap
- Progressive 4-phase curriculum tailored to the candidate's exact missing skills:
  - **Phase 1 (Weeks 1-2)**: Core Syntax & Foundational Gaps
  - **Phase 2 (Weeks 3-4)**: Framework Fluency & State Architecture
  - **Phase 3 (Weeks 5-6)**: DevOps, Containerization (Docker) & Cloud Deployment
  - **Phase 4 (Weeks 7-8)**: System Design, Capstone Integration & Interview Polish
- Includes concrete **Portfolio Mini-Project blueprints** for each phase.

### 5. Categorized Interview Question Bank
- 12+ targeted interview questions categorized into:
  - **Core Technical**
  - **Resume Project Deep-Dive**
  - **Behavioral (STAR Method)**
  - **System Design & Architecture**
- Expandable **Model Tips** showing expected keywords and answer frameworks.

### 6. 🎙️ Interactive AI Mock Interviewer Agent
- **Conversational Simulator**: Simulates a live technical interview session.
- **Voice or Typed Responses**: Speak directly into the microphone via the Web Speech API or type your technical answer.
- **Real-Time Rubric Scoring**:
  - Score out of 10 with colored verdict badge.
  - Identifies specific points you articulated well.
  - Exposes missing technical keywords and concepts.
  - Shows an **Exemplary Model Answer** (how a Staff/Senior Engineer would respond).
- **Session Performance Report Card**: Generates a cumulative score and hiring readiness verdict.

### 7. ✏️ Google X-Y-Z Resume Bullet Rewriter
- Transforms weak bullet points into high-impact accomplishments using Google's formula:
  > *"Accomplished [X] as measured by [Y], by doing [Z]"*
- Generates 3 variations: Metrics & Impact, Architecture & Scalability, and Production Quality.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **Document Processing** | `pypdf`, `python-docx` |
| **NLP & Vectors** | `scikit-learn` (TF-IDF, Cosine Similarity), Regex Ontology |
| **LLM Orchestration** | Google Gemini (`gemini-2.0-flash`), OpenAI (`gpt-4o-mini`), Groq (`llama-3.3-70b`), and Built-in Smart Local AI Engine |
| **Frontend** | Responsive Glassmorphism SPA, Tailwind CSS CDN, Lucide Icons, Chart.js (Radar Chart), Web Speech API |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run.py
```
The server will start at `http://127.0.0.1:8000` and automatically open your default browser.

### 3. (Optional) Configure External LLM APIs
By default, CareerLens AI uses its **Smart Local Heuristic Engine**, which operates offline with zero configuration and zero API keys required.

To enable live Google Gemini, OpenAI, or Groq models:
- Click the **Provider button** in the top navigation bar of the web app.
- Select your provider and enter your API key.
- Or set environment variables in your terminal:
  ```bash
  set GEMINI_API_KEY="your-gemini-key"
  # or
  set OPENAI_API_KEY="your-openai-key"
  # or
  set GROQ_API_KEY="your-groq-key"
  ```

---

## 🧪 Automated Testing
Run the comprehensive integration test suite:
```bash
python test_endpoints.py
```
Validates all 6 REST endpoints, document parsers, and mock interview state flow.

---

## 💡 Project Pitch for Interviews & Presentations

> *"Instead of building a simple resume keyword matcher, I architected CareerLens AI as an end-to-end AI Career Guidance Agent. It pairs ATS document parsing with semantic cosine similarity and an LLM orchestration layer. It not only identifies missing technical competencies, but also generates a customized 8-week bridge curriculum and conducts interactive AI Mock Interviews where candidates can speak their answers and receive real-time rubric feedback and Staff-Engineer model answers."*
