"""Interactive Mock Interviewer Agent for CareerLens AI.
Manages mock interview sessions, turn-by-turn question flow, and real-time rubric scoring.
"""

import uuid
import time
from typing import Dict, List, Any, Optional
from backend.llm_engine import llm_agent

# In-memory session store (can be persisted to SQLite or MongoDB if needed)
MOCK_SESSIONS: Dict[str, Dict[str, Any]] = {}


class MockInterviewSession:
    def __init__(self, role: str, candidate_name: str, questions: List[Dict[str, Any]], session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.role = role or "Software Engineer"
        self.candidate_name = candidate_name or "Candidate"
        self.questions = questions or []
        self.current_index = 0
        self.started_at = time.time()
        self.evaluations: List[Dict[str, Any]] = []

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def submit_answer(self, candidate_answer: str) -> Dict[str, Any]:
        curr_q = self.get_current_question()
        if not curr_q:
            return {"status": "completed", "message": "Interview session already completed."}

        # Evaluate the answer with AI agent
        eval_result = llm_agent.evaluate_mock_answer(curr_q, candidate_answer, self.role)
        
        entry = {
            "question_id": curr_q.get("id", self.current_index + 1),
            "category": curr_q.get("category", "Technical"),
            "question": curr_q.get("question", ""),
            "candidate_answer": candidate_answer,
            "evaluation": eval_result,
            "timestamp": time.time()
        }
        self.evaluations.append(entry)
        self.current_index += 1

        next_q = self.get_current_question()
        is_finished = next_q is None

        return {
            "status": "in_progress" if not is_finished else "completed",
            "evaluated_entry": entry,
            "next_question": next_q,
            "progress": {
                "current": self.current_index,
                "total": len(self.questions),
                "is_finished": is_finished
            }
        }

    def generate_report_card(self) -> Dict[str, Any]:
        if not self.evaluations:
            return {
                "session_id": self.session_id,
                "candidate_name": self.candidate_name,
                "role": self.role,
                "total_questions": len(self.questions),
                "completed_questions": 0,
                "average_score": 0.0,
                "performance_verdict": "Not Started"
            }

        scores = [e["evaluation"]["score"] for e in self.evaluations]
        avg_score = round(sum(scores) / len(scores), 1)

        all_strengths = []
        for e in self.evaluations:
            all_strengths.extend(e["evaluation"].get("strengths", []))

        all_improvements = []
        for e in self.evaluations:
            all_improvements.extend(e["evaluation"].get("improvement_areas", []))

        verdict = (
            "Ready for Onsite / Outstanding Performance" if avg_score >= 8.5
            else ("Solid Candidate / Good Command" if avg_score >= 7.0
            else ("Promising / Needs More Technical Depth" if avg_score >= 5.0
            else "Needs Foundational Preparation"))
        )

        return {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "role": self.role,
            "total_questions": len(self.questions),
            "completed_questions": len(self.evaluations),
            "average_score": avg_score,
            "score_out_of_100": int(avg_score * 10),
            "performance_verdict": verdict,
            "top_strengths": list(dict.fromkeys(all_strengths))[:4],
            "key_growth_areas": list(dict.fromkeys(all_improvements))[:4],
            "turn_history": self.evaluations
        }


def create_interview_session(role: str, candidate_name: str, questions: List[Dict[str, Any]]) -> MockInterviewSession:
    # Select first 5-8 questions for a focused session
    selected_questions = questions[:6] if len(questions) > 6 else questions
    session = MockInterviewSession(role, candidate_name, selected_questions)
    MOCK_SESSIONS[session.session_id] = session
    return session


def get_interview_session(session_id: str) -> Optional[MockInterviewSession]:
    return MOCK_SESSIONS.get(session_id)
