"""Multi-Provider LLM & AI Career Agent Engine for CareerLens AI.
Supports Google Gemini, OpenAI, Groq, and a Built-In Smart Local Engine.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

# Attempt optional imports
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None


class LLMEngine:
    def __init__(self, provider: str = "smart_local", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        
        # Determine active provider
        if not self.api_key or self.provider == "smart_local":
            self.provider = "smart_local"
            
    def set_provider(self, provider: str, api_key: Optional[str] = None):
        self.provider = provider.lower()
        if api_key:
            self.api_key = api_key

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        """Call Google Gemini API."""
        if not self.api_key:
            raise ValueError("Gemini API key is required.")
        
        # Try google-genai modern client
        try:
            client = genai.Client(api_key=self.api_key)
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            # Fallback to google.generativeai legacy if present
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=self.api_key)
                model = legacy_genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(f"{system_instruction}\n\n{prompt}")
                return resp.text
            except Exception:
                raise e

    def _call_openai_compatible(self, prompt: str, system_instruction: str = "", base_url: Optional[str] = None, model: str = "gpt-4o-mini") -> str:
        """Call OpenAI or Groq API."""
        if not self.api_key:
            raise ValueError("API key is required.")
        
        client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.4
        )
        return resp.choices[0].message.content or ""

    def _generate_with_llm(self, prompt: str, system_instruction: str = "") -> str:
        """Route to appropriate LLM or raise to trigger smart local fallback."""
        if self.provider == "gemini":
            return self._call_gemini(prompt, system_instruction)
        elif self.provider == "openai":
            return self._call_openai_compatible(prompt, system_instruction, model="gpt-4o-mini")
        elif self.provider == "groq":
            return self._call_openai_compatible(
                prompt,
                system_instruction,
                base_url="https://api.groq.com/openai/v1",
                model="llama-3.3-70b-versatile"
            )
        else:
            raise NotImplementedError("Using smart local engine")

    def generate_career_analysis(self, resume_text: str, jd_text: str, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive executive critique and gap insights."""
        matching_names = [s["name"] for s in match_data["matching_skills"]]
        missing_names = [s["name"] for s in match_data["missing_skills"]]
        overall_score = match_data["overall_score"]
        
        if self.provider != "smart_local" and self.api_key:
            try:
                system_prompt = (
                    "You are a Principal Tech Recruiter and Career Coach. Analyze the resume against the job description. "
                    "Return ONLY valid JSON matching this schema: "
                    '{"executive_summary": "string", "strengths": ["string"], "red_flags": ["string"], "quick_wins": ["string"]}'
                )
                user_prompt = f"""
Resume:
{resume_text[:2000]}

Job Description:
{jd_text[:1500]}

Matched Skills: {', '.join(matching_names)}
Missing Skills: {', '.join(missing_names)}
Match Score: {overall_score}%
"""
                raw_text = self._generate_with_llm(user_prompt, system_prompt)
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception as e:
                pass  # Fall back to smart local logic

        # Smart Local Engine: Rule-based intelligent synthesis
        strengths = []
        if matching_names:
            strengths.append(f"Strong foundation in core technical competencies: {', '.join(matching_names[:4])}.")
        if match_data["ats_score"] >= 80:
            strengths.append("High ATS compliance with quantifiable project metrics and crisp technical action verbs.")
        else:
            strengths.append("Clear educational background and demonstrable project implementations.")
        if "REST API" in matching_names or "Spring Boot" in matching_names:
            strengths.append("Hands-on backend architecture experience with API design and database integrations.")
        if len(matching_names) >= 5:
            strengths.append(f"Demonstrated proficiency in {len(matching_names)} technologies directly requested in the job description.")

        red_flags = []
        if missing_names:
            high_pri = [s["name"] for s in match_data["missing_skills"] if s.get("priority") == "High"]
            red_flags.append(f"Critical requirement gap in key technologies: {', '.join((high_pri or missing_names)[:4])}.")
        if "Docker" in missing_names or "CI/CD" in missing_names or "AWS" in missing_names:
            red_flags.append("Limited exposure to modern DevOps & Cloud containerization workflows (Docker/Cloud).")
        if "React" in missing_names or "TypeScript" in missing_names:
            red_flags.append("Job calls for client-side modern UI engineering, which is currently less evident in the resume.")
        if match_data["overall_score"] < 60:
            red_flags.append("Resume requires explicit tailoring to highlight relevant projects aligning directly with the target JD.")

        quick_wins = [
            f"Add a dedicated project or case study specifically implementing {missing_names[0] if missing_names else 'Cloud Deployment'}.",
            "Revise existing project bullet points to emphasize architectural trade-offs, performance gains, and scale metrics.",
            f"Highlight familiarity with {', '.join(matching_names[:3])} prominently in your top summary section to pass initial recruiter scans.",
            "Deploy your existing GitHub projects on live URLs (e.g. Vercel, Render, AWS Free Tier) and link them directly in the resume header."
        ]

        summary_text = (
            f"The candidate demonstrates a solid match score of {overall_score}%, with notable strengths in {', '.join(matching_names[:3]) if matching_names else 'core CS fundamentals'}. "
            f"To become a top-tier candidate for this role, the primary focus must be closing the gap on {', '.join(missing_names[:3]) if missing_names else 'advanced distributed systems'} "
            "and highlighting end-to-end full-stack integration in portfolio projects."
        )

        return {
            "executive_summary": summary_text,
            "strengths": strengths[:4],
            "red_flags": red_flags[:4],
            "quick_wins": quick_wins
        }

    def generate_learning_roadmap(self, missing_skills: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
        """Generate a progressive, 4-phase learning roadmap with actionable projects."""
        missing_names = [s["name"] for s in missing_skills]
        if not missing_names:
            missing_names = ["Docker", "AWS", "CI/CD", "System Design", "Microservices"]

        # If LLM available, try generating dynamic roadmap
        if self.provider != "smart_local" and self.api_key:
            try:
                system_prompt = (
                    "You are a Staff Technical Mentor. Generate a 4-phase learning roadmap to bridge missing skills for this role. "
                    "Return ONLY a JSON array where each object has: "
                    '{"phase": "string", "duration": "string", "title": "string", "focus_skills": ["string"], "topics": ["string"], "mini_project": {"title": "string", "description": "string", "tech_stack": "string"}}'
                )
                user_prompt = f"Role: {target_role}\nMissing Skills to learn: {', '.join(missing_names)}"
                raw_text = self._generate_with_llm(user_prompt, system_prompt)
                json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception:
                pass

        # Smart Local Engine: Tailored high-quality curated curriculum
        # Distribute missing skills across 4 phases
        s_count = len(missing_names)
        p1_skills = missing_names[:max(1, s_count // 4)]
        p2_skills = missing_names[max(1, s_count // 4): max(2, (s_count * 2) // 4)]
        p3_skills = missing_names[max(2, (s_count * 2) // 4): max(3, (s_count * 3) // 4)]
        p4_skills = missing_names[max(3, (s_count * 3) // 4):] or ["System Design & Mock Practice"]

        roadmap = [
            {
                "phase": "Phase 1: High-Priority Core Gaps",
                "duration": "Weeks 1 - 2",
                "title": f"Mastering Foundational Gaps ({', '.join(p1_skills)})",
                "focus_skills": p1_skills,
                "topics": [
                    f"Core architecture, lifecycle, and syntax of {p1_skills[0] if p1_skills else 'Target Tech'}",
                    "Hands-on coding exercises, asynchronous patterns, and API integration",
                    "Unit testing and writing clean, modular components"
                ],
                "mini_project": {
                    "title": f"{p1_skills[0] if p1_skills else 'Fullstack'} Micro-App",
                    "description": f"Build a focused CRUD application utilizing {', '.join(p1_skills)} with robust data validation and error handling.",
                    "tech_stack": ", ".join(p1_skills) + ", Git"
                }
            },
            {
                "phase": "Phase 2: Architectural & Framework Integration",
                "duration": "Weeks 3 - 4",
                "title": f"Framework Fluency & State Architecture ({', '.join(p2_skills)})",
                "focus_skills": p2_skills,
                "topics": [
                    f"Advanced design patterns in {p2_skills[0] if p2_skills else 'Frontend/Backend'}",
                    "Global state management, caching strategies, and data persistence",
                    "Secure authentication (JWT / OAuth2) and API gateway communication"
                ],
                "mini_project": {
                    "title": "Interactive Real-Time Dashboard",
                    "description": f"Develop a multi-tenant dashboard incorporating {', '.join(p2_skills)} with role-based access control and analytics charts.",
                    "tech_stack": ", ".join(p2_skills) + ", RESTful APIs"
                }
            },
            {
                "phase": "Phase 3: DevOps, Cloud & Containerization",
                "duration": "Weeks 5 - 6",
                "title": f"Cloud Deployment & Automation ({', '.join(p3_skills)})",
                "focus_skills": p3_skills,
                "topics": [
                    "Multi-stage Dockerfile builds and image optimization",
                    "Automated CI/CD pipelines via GitHub Actions (lint, test, build)",
                    "Cloud deployment (AWS EC2/S3/ECS or GCP Cloud Run) and environment secret management"
                ],
                "mini_project": {
                    "title": "Production Containerized Microservice",
                    "description": f"Containerize your previous applications with Docker Compose, automated GitHub Actions testing, and deployment to the cloud.",
                    "tech_stack": "Docker, GitHub Actions, " + (", ".join(p3_skills))
                }
            },
            {
                "phase": "Phase 4: Capstone Integration & Interview Readiness",
                "duration": "Weeks 7 - 8",
                "title": "Full-Scale Capstone & System Design Polish",
                "focus_skills": p4_skills + ["System Design", "Mock Interviews"],
                "topics": [
                    "High-level system design: load balancers, caching (Redis), database sharding & replication",
                    "LeetCode/HackerRank targeted DSA revision (Graph, Tree, Dynamic Programming, Heap)",
                    "Behavioral STAR stories alignment with hiring manager rubrics"
                ],
                "mini_project": {
                    "title": "Production-Grade Capstone Showcase",
                    "description": "An end-to-end full-stack distributed system uniting all learned skills, complete with architecture diagrams, Swagger documentation, and automated tests.",
                    "tech_stack": "Full Stack + Docker + Cloud"
                }
            }
        ]
        return roadmap

    def generate_interview_questions(self, resume_text: str, jd_text: str, match_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate categorized interview questions targeting candidate's background and JD gaps."""
        matching_names = [s["name"] for s in match_data["matching_skills"]]
        missing_names = [s["name"] for s in match_data["missing_skills"]]

        if self.provider != "smart_local" and self.api_key:
            try:
                system_prompt = (
                    "You are a Senior Engineering Hiring Manager at a top tech company. Generate 12 targeted interview questions for this candidate. "
                    "Return ONLY a JSON array of objects with: "
                    '{"id": int, "category": "Technical"|"Resume Project"|"Behavioral"|"System Design", "question": "string", "why_asked": "string", "expected_keywords": ["string"], "model_answer_tip": "string"}'
                )
                user_prompt = f"Resume snippet: {resume_text[:1200]}\nJD snippet: {jd_text[:1200]}\nMatched skills: {', '.join(matching_names[:5])}\nMissing skills: {', '.join(missing_names[:5])}"
                raw_text = self._generate_with_llm(user_prompt, system_prompt)
                json_match = re.search(r"\[.*\]", raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception:
                pass

        # Smart Local Engine: Curated role-specific questions
        primary_match = matching_names[0] if matching_names else "Java"
        second_match = matching_names[1] if len(matching_names) > 1 else "SQL"
        primary_gap = missing_names[0] if missing_names else "Docker"
        second_gap = missing_names[1] if len(missing_names) > 1 else "React"

        return [
            # Technical Questions
            {
                "id": 1,
                "category": "Technical",
                "question": f"How do you manage database transaction boundaries and isolation levels in {primary_match} applications to prevent dirty reads and race conditions?",
                "why_asked": f"Assesses deep understanding of backend integrity, concurrency, and {primary_match} persistence frameworks.",
                "expected_keywords": ["ACID", "Isolation Levels", "@Transactional", "Dirty Read", "Optimistic vs Pessimistic Locking", "Connection Pool"],
                "model_answer_tip": "Define ACID properties, mention how framework proxies handle transaction rollbacks on unchecked exceptions, and explain Read Committed vs Repeatable Read."
            },
            {
                "id": 2,
                "category": "Technical",
                "question": f"The job description requires experience with {primary_gap}. How would you design and implement a solution with {primary_gap}, or bridge your existing knowledge from {primary_match}?",
                "why_asked": f"Tests candidate's adaptability to bridge their missing skill ({primary_gap}) and technical aptitude.",
                "expected_keywords": [primary_gap, "Best Practices", "Architecture", "Learning Agility", "Trade-offs"],
                "model_answer_tip": f"Acknowledge familiarity, explain theoretical foundations, compare it to concepts in {primary_match}, and describe a small prototype you recently built or studied."
            },
            {
                "id": 3,
                "category": "Technical",
                "question": f"Explain the internal implementation of HashMap / Dictionary in your primary language and how hash collisions are resolved.",
                "why_asked": "Core Data Structures test to verify foundational computer science fundamentals.",
                "expected_keywords": ["Hash Function", "Bucket Array", "Collision Resolution", "Chaining", "Red-Black Tree", "Load Factor", "O(1) average lookup"],
                "model_answer_tip": "Walk through hashCode() & equals(), describe chaining with linked lists, treeification thresholds (e.g. 8 in Java), and rehashing upon crossing 0.75 load factor."
            },
            {
                "id": 4,
                "category": "Technical",
                "question": f"How do you optimize an SQL query that joins multiple large tables when execution times spike under production traffic?",
                "why_asked": "Assesses real-world database performance tuning and SQL query execution analysis.",
                "expected_keywords": ["EXPLAIN ANALYZE", "B-Tree Indexing", "Composite Index", "Full Table Scan", "Denormalization", "Covering Index"],
                "model_answer_tip": "Start with running EXPLAIN to check query execution plans, verify existing indexes, eliminate SELECT *, and discuss query restructuring or caching with Redis."
            },

            # Resume Project Questions
            {
                "id": 5,
                "category": "Resume Project",
                "question": "Can you walk me through the architecture of your featured project, including the key design trade-offs you made?",
                "why_asked": "Evaluates architectural ownership and whether the candidate truly built the project on their resume.",
                "expected_keywords": ["Architecture", "Client-Server", "Database Choice", "Trade-off", "Bottleneck", "Scalability"],
                "model_answer_tip": "Use the Problem → Solution → Architecture → Metrics flow. Explicitly mention why you selected the tech stack over alternatives."
            },
            {
                "id": 6,
                "category": "Resume Project",
                "question": "Tell me about a challenging technical bug or performance bottleneck you encountered in your projects and how you diagnosed it.",
                "why_asked": "Verifies debugging methodology, root cause analysis, and resilience under obstacles.",
                "expected_keywords": ["Profiling", "Logs", "Root Cause Analysis", "Reproducing the Bug", "Verification", "Fix Impact"],
                "model_answer_tip": "Structure using STAR method. Focus on the analytical steps you took to isolate the bug rather than guessing."
            },
            {
                "id": 7,
                "category": "Resume Project",
                "question": "How did you test your application for edge cases and ensure reliability before considering it production-ready?",
                "why_asked": "Checks quality mindset, test automation, and code validation standards.",
                "expected_keywords": ["Unit Testing", "Mocking", "Boundary Values", "Integration Tests", "CI Validation"],
                "model_answer_tip": "Discuss unit testing with mocks, integration testing with in-memory DB or test containers, and testing null/overflow boundary scenarios."
            },

            # Behavioral (STAR Method)
            {
                "id": 8,
                "category": "Behavioral",
                "question": "Tell me about a time you had to deliver a feature with an unfamiliar technology on a tight deadline.",
                "why_asked": "Gauges learning agility, time management, and ability to handle ambiguous technical requirements.",
                "expected_keywords": ["STAR Method", "Prioritization", "Rapid Prototyping", "Documentation", "Team Collaboration"],
                "model_answer_tip": "Situation: tight deadline with unfamiliar tool. Task: deliver milestone. Action: broke learning into MVPs, read docs, consulted seniors. Result: on-time delivery with zero regression."
            },
            {
                "id": 9,
                "category": "Behavioral",
                "question": "Describe a situation where you had a technical disagreement with a peer or senior on code implementation. How was it resolved?",
                "why_asked": "Evaluates emotional intelligence, constructive communication, and objective decision-making.",
                "expected_keywords": ["Data-Driven", "Benchmarking", "Respectful Communication", "Code Review", "Team Alignment"],
                "model_answer_tip": "Emphasize focusing on data, benchmarks, and project goals rather than personal ego. Explain how you reached a collaborative consensus."
            },
            {
                "id": 10,
                "category": "Behavioral",
                "question": "Give an example of a mistake you made in code or project planning and what you learned from the experience.",
                "why_asked": "Tests humility, accountability, and continuous improvement culture.",
                "expected_keywords": ["Accountability", "Blameless Post-Mortem", "Remediation", "Safeguards Implemented"],
                "model_answer_tip": "Be honest about the mistake, demonstrate prompt ownership, and explain the preventative checks (e.g. linter, test guard, checklist) you added."
            },

            # System Design & Architecture
            {
                "id": 11,
                "category": "System Design",
                "question": f"How would you design a scalable URL shortener (like Bitly) or Notification service handling 10,000 requests per second?",
                "why_asked": "Assesses distributed system thinking, capacity estimation, and architectural trade-offs.",
                "expected_keywords": ["Hashing (Base62/MD5)", "Database Sharding", "Redis Cache", "Rate Limiting", "Load Balancer", "High Availability"],
                "model_answer_tip": "Clarify functional & non-functional requirements, sketch API endpoints, estimate storage/throughput, choose DB (SQL vs NoSQL), and introduce caching layers."
            },
            {
                "id": 12,
                "category": "System Design",
                "question": f"If this application needs to support real-time user updates (like order tracking or live status), would you choose WebSockets, SSE, or Polling, and why?",
                "why_asked": "Tests protocol choices, network overhead awareness, and full-stack real-time considerations.",
                "expected_keywords": ["WebSockets", "Server-Sent Events (SSE)", "Long Polling", "Full Duplex", "Connection Overhead", "HTTP/2"],
                "model_answer_tip": "Compare: Polling causes heavy HTTP overhead; SSE is perfect for unidirectional server-to-client streams; WebSockets is ideal for bidirectional real-time communication."
            }
        ]

    def evaluate_mock_answer(self, question_obj: Dict[str, Any], candidate_answer: str, role: str) -> Dict[str, Any]:
        """Evaluate a candidate's answer during the interactive AI Mock Interview."""
        q_text = question_obj.get("question", "")
        expected_kws = question_obj.get("expected_keywords", [])
        
        if self.provider != "smart_local" and self.api_key:
            try:
                system_prompt = (
                    "You are an expert technical interviewer. Evaluate the candidate's answer. "
                    "Return ONLY valid JSON with: "
                    '{"score": int (1-10), "verdict": "string", "strengths": ["string"], "improvement_areas": ["string"], "matched_keywords": ["string"], "missing_keywords": ["string"], "exemplary_answer": "string"}'
                )
                user_prompt = f"Role: {role}\nQuestion: {q_text}\nExpected Concepts: {', '.join(expected_kws)}\nCandidate Answer: {candidate_answer}"
                raw_text = self._generate_with_llm(user_prompt, system_prompt)
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception:
                pass

        # Smart Local Engine: Heuristic evaluation
        ans_lower = candidate_answer.lower()
        matched_kws = [kw for kw in expected_kws if kw.lower() in ans_lower]
        missing_kws = [kw for kw in expected_kws if kw.lower() not in ans_lower]
        
        word_count = len(candidate_answer.split())
        
        # Scoring algorithm
        base_score = 4
        if word_count >= 30:
            base_score += 1
        if word_count >= 60:
            base_score += 1
        if expected_kws:
            kw_ratio = len(matched_kws) / len(expected_kws)
            base_score += int(kw_ratio * 4)
            
        final_score = max(3, min(10, base_score))
        
        strengths = []
        if word_count >= 40:
            strengths.append("Structured and articulate explanation with good conversational flow.")
        if matched_kws:
            strengths.append(f"Accurately incorporated essential technical terminology: {', '.join(matched_kws)}.")
        else:
            strengths.append("Demonstrated foundational conceptual awareness.")

        improvements = []
        if missing_kws:
            improvements.append(f"Incorporate key industry concepts: {', '.join(missing_kws[:3])}.")
        if word_count < 45:
            improvements.append("Expand on real-world implementation details, edge cases, and personal experience.")
        else:
            improvements.append("Conclude with the concrete outcome or measurable metric resulting from your technical choice.")

        exemplary = (
            f"An exemplary answer should clearly address the core mechanism: begin with the high-level principle, "
            f"mention crucial technical specifics ({', '.join(expected_kws[:3]) if expected_kws else 'architectural choices'}), "
            f"and conclude with practical trade-offs like performance, maintainability, and scalability considerations."
        )

        return {
            "score": final_score,
            "verdict": "Exceptional" if final_score >= 9 else ("Strong" if final_score >= 7 else ("Acceptable" if final_score >= 5 else "Needs Polish")),
            "strengths": strengths,
            "improvement_areas": improvements,
            "matched_keywords": matched_kws,
            "missing_keywords": missing_kws,
            "exemplary_answer": exemplary
        }

    def rewrite_resume_bullet(self, original_bullet: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Rewrite a weak resume bullet point into 3 high-impact versions using the X-Y-Z formula."""
        kw_str = ", ".join(target_keywords[:3]) if target_keywords else "scalability, performance"
        
        if self.provider != "smart_local" and self.api_key:
            try:
                system_prompt = (
                    "You are an executive resume writer. Rewrite the given bullet point into 3 impactful bullet points "
                    "following Google's XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. "
                    "Return ONLY valid JSON with: "
                    '{"original": "string", "rewrites": [{"style": "string", "text": "string", "highlight": "string"}]}'
                )
                user_prompt = f"Original bullet: {original_bullet}\nTarget keywords: {kw_str}"
                raw_text = self._generate_with_llm(user_prompt, system_prompt)
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception:
                pass

        # Smart Local Engine: Generated variations
        clean_bullet = original_bullet.strip("-•* ")
        clean_bullet = clean_bullet[0].lower() + clean_bullet[1:] if clean_bullet else "built an application"
        
        return {
            "original": original_bullet,
            "rewrites": [
                {
                    "style": "Metrics & Impact Focused (Google X-Y-Z)",
                    "text": f"Engineered resilient solutions to {clean_bullet}, improving overall processing throughput by 32% and reducing endpoint latency from 450ms to 110ms.",
                    "highlight": "Emphasizes quantifiable performance enhancements and measurable business impact."
                },
                {
                    "style": "Technical Architecture & Scalability",
                    "text": f"Architected and deployed {clean_bullet} utilizing {kw_str}, implementing robust caching and normalized database indexing to support 15,000+ concurrent requests.",
                    "highlight": "Positions you as a high-level system architect with deep tech stack fluency."
                },
                {
                    "style": "Production Reliability & Best Practices",
                    "text": f"Spearheaded the development of {clean_bullet}, incorporating automated CI/CD pipeline validations and comprehensive unit test suites reaching 85%+ code coverage.",
                    "highlight": "Demonstrates mature engineering standards, automated testing, and production quality."
                }
            ]
        }


# Global singleton instance
llm_agent = LLMEngine()


if __name__ == "__main__":
    from backend.sample_data import SAMPLE_RESUMES, SAMPLE_JDS
    from backend.matcher import analyze_skill_gaps
    res = SAMPLE_RESUMES["sde_fresher"]["text"]
    jd = SAMPLE_JDS["google_sde"]["text"]
    match_data = analyze_skill_gaps(res, jd)
    critique = llm_agent.generate_career_analysis(res, jd, match_data)
    print("Critique Executive Summary:", critique["executive_summary"])
    print("Roadmap Phases:", len(llm_agent.generate_learning_roadmap(match_data["missing_skills"], "SDE-1")))
    print("LLM Engine test successful!")
