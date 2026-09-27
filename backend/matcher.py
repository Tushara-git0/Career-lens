"""Semantic Matching & Skill Gap Analysis Engine for CareerLens AI.
Combines ontology-based extraction, fuzzy alias mapping,
and TF-IDF cosine vector similarity.
"""

import re
from typing import Dict, List, Set, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Comprehensive Canonical Skill Ontology & Aliases
SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Programming Languages
    "Java": {"category": "Languages", "aliases": ["core java", "java 8", "java 11", "java 17", "java 21"]},
    "Python": {"category": "Languages", "aliases": ["python 3", "py"]},
    "JavaScript": {"category": "Languages", "aliases": ["js", "es6", "es6+", "vanilla js", "modern javascript"]},
    "TypeScript": {"category": "Languages", "aliases": ["ts"]},
    "C++": {"category": "Languages", "aliases": ["cpp", "c plus plus"]},
    "C": {"category": "Languages", "aliases": []},
    "C#": {"category": "Languages", "aliases": ["csharp", ".net c#"]},
    "Go": {"category": "Languages", "aliases": ["golang"]},
    "Rust": {"category": "Languages", "aliases": []},
    "SQL": {"category": "Languages", "aliases": ["t-sql", "pl/sql", "structured query language"]},
    "HTML5": {"category": "Languages", "aliases": ["html", "html/css"]},
    "CSS3": {"category": "Languages", "aliases": ["css", "styling"]},
    "PHP": {"category": "Languages", "aliases": []},
    "Kotlin": {"category": "Languages", "aliases": []},
    "Swift": {"category": "Languages", "aliases": []},
    "R": {"category": "Languages", "aliases": ["r programming"]},

    # Frontend Frameworks & Libraries
    "React": {"category": "Frontend", "aliases": ["react.js", "reactjs", "react native"]},
    "Next.js": {"category": "Frontend", "aliases": ["nextjs", "next"]},
    "Angular": {"category": "Frontend", "aliases": ["angular.js", "angularjs", "angular 2+"]},
    "Vue.js": {"category": "Frontend", "aliases": ["vue", "vuejs", "nuxt", "nuxtjs"]},
    "Redux": {"category": "Frontend", "aliases": ["redux toolkit", "rtk", "react redux"]},
    "Tailwind CSS": {"category": "Frontend", "aliases": ["tailwind", "tailwindcss"]},
    "Bootstrap": {"category": "Frontend", "aliases": ["bootstrap 5", "bootstrap 4"]},
    "Zustand": {"category": "Frontend", "aliases": []},
    "React Query": {"category": "Frontend", "aliases": ["tanstack query", "react-query"]},
    "Webpack": {"category": "Frontend", "aliases": []},
    "Vite": {"category": "Frontend", "aliases": []},

    # Backend Frameworks
    "Spring Boot": {"category": "Backend", "aliases": ["springboot", "spring framework", "spring mvc", "spring"]},
    "Node.js": {"category": "Backend", "aliases": ["nodejs", "node"]},
    "Express.js": {"category": "Backend", "aliases": ["express", "expressjs"]},
    "Django": {"category": "Backend", "aliases": ["django rest framework", "drf"]},
    "FastAPI": {"category": "Backend", "aliases": ["fast-api"]},
    "Flask": {"category": "Backend", "aliases": []},
    "Hibernate": {"category": "Backend", "aliases": ["hibernate/jpa", "jpa"]},
    "ASP.NET": {"category": "Backend", "aliases": [".net core", "asp.net core", ".net"]},
    "NestJS": {"category": "Backend", "aliases": ["nest.js"]},
    "GraphQL": {"category": "Backend", "aliases": ["apollo graphql"]},
    "REST API": {"category": "Backend", "aliases": ["restful api", "rest apis", "restful", "rest api development", "restful web services"]},
    "Microservices": {"category": "Backend", "aliases": ["microservice architecture", "distributed systems", "micro-services"]},
    "WebSockets": {"category": "Backend", "aliases": ["socket.io", "websockets"]},
    "gRPC": {"category": "Backend", "aliases": ["rpc"]},

    # Databases & Storage
    "MySQL": {"category": "Database", "aliases": []},
    "PostgreSQL": {"category": "Database", "aliases": ["postgres", "psql"]},
    "MongoDB": {"category": "Database", "aliases": ["mongo", "nosql mongodb"]},
    "Redis": {"category": "Database", "aliases": ["redis cache"]},
    "SQLite": {"category": "Database", "aliases": []},
    "Elasticsearch": {"category": "Database", "aliases": ["elastic search", "elk"]},
    "Cassandra": {"category": "Database", "aliases": ["apache cassandra"]},
    "DynamoDB": {"category": "Database", "aliases": ["aws dynamodb"]},
    "Oracle DB": {"category": "Database", "aliases": ["oracle database", "oracle sql"]},
    "Snowflake": {"category": "Database", "aliases": []},

    # Cloud & DevOps
    "AWS": {"category": "Cloud & DevOps", "aliases": ["amazon web services", "aws ec2", "aws s3", "aws lambda", "cloud (aws)"]},
    "Docker": {"category": "Cloud & DevOps", "aliases": ["containerization", "containers"]},
    "Kubernetes": {"category": "Cloud & DevOps", "aliases": ["k8s", "container orchestration"]},
    "Git": {"category": "Cloud & DevOps", "aliases": ["github", "gitlab", "version control"]},
    "CI/CD": {"category": "Cloud & DevOps", "aliases": ["ci cd", "continuous integration", "github actions", "jenkins", "gitlab ci"]},
    "Linux": {"category": "Cloud & DevOps", "aliases": ["unix", "ubuntu", "bash", "shell scripting"]},
    "Terraform": {"category": "Cloud & DevOps", "aliases": ["iac", "infrastructure as code"]},
    "Google Cloud": {"category": "Cloud & DevOps", "aliases": ["gcp", "google cloud platform"]},
    "Azure": {"category": "Cloud & DevOps", "aliases": ["microsoft azure"]},

    # AI, ML & Data Science
    "Machine Learning": {"category": "AI & Data", "aliases": ["ml", "predictive modeling"]},
    "Deep Learning": {"category": "AI & Data", "aliases": ["neural networks", "dl"]},
    "PyTorch": {"category": "AI & Data", "aliases": ["torch"]},
    "TensorFlow": {"category": "AI & Data", "aliases": ["tf", "keras"]},
    "Pandas": {"category": "AI & Data", "aliases": []},
    "NumPy": {"category": "AI & Data", "aliases": []},
    "Scikit-Learn": {"category": "AI & Data", "aliases": ["sklearn", "scikit learn"]},
    "NLP": {"category": "AI & Data", "aliases": ["natural language processing", "spacy", "nltk"]},
    "LLM": {"category": "AI & Data", "aliases": ["large language models", "generative ai", "langchain", "llamaindex", "rag"]},
    "Computer Vision": {"category": "AI & Data", "aliases": ["opencv", "cv"]},
    "Tableau": {"category": "AI & Data", "aliases": []},
    "Power BI": {"category": "AI & Data", "aliases": ["powerbi", "dax"]},

    # Testing & Tooling
    "JUnit": {"category": "Testing & Tools", "aliases": ["junit 5", "unit testing"]},
    "Mockito": {"category": "Testing & Tools", "aliases": []},
    "Jest": {"category": "Testing & Tools", "aliases": ["jest testing"]},
    "PyTest": {"category": "Testing & Tools", "aliases": ["pytest"]},
    "Postman": {"category": "Testing & Tools", "aliases": ["api testing"]},
    "Maven": {"category": "Testing & Tools", "aliases": ["gradle"]},
    "JIRA": {"category": "Testing & Tools", "aliases": ["confluence", "jira tracking"]},

    # Core CS & Fundamentals
    "Data Structures & Algorithms": {"category": "Core CS", "aliases": ["data structures", "algorithms", "dsa", "problem solving"]},
    "Object-Oriented Programming": {"category": "Core CS", "aliases": ["oop", "oops", "object oriented design", "ood"]},
    "Database Management Systems": {"category": "Core CS", "aliases": ["dbms", "database design", "query optimization", "normalization"]},
    "Operating Systems": {"category": "Core CS", "aliases": ["os", "multithreading", "concurrency"]},
    "Computer Networks": {"category": "Core CS", "aliases": ["networking", "tcp/ip", "http/https"]},
    "System Design": {"category": "Core CS", "aliases": ["system architecture", "high level design", "low level design", "hld", "lld"]},
    "Agile / Scrum": {"category": "Core CS", "aliases": ["agile", "scrum", "sprints"]}
}


def _build_search_regex(skill_name: str, aliases: List[str]) -> re.Pattern:
    """Build a regex pattern to safely match words without false positive substrings."""
    all_terms = [skill_name] + aliases
    escaped = []
    for term in sorted(all_terms, key=len, reverse=True):
        esc = re.escape(term)
        # Handle cases like C++ or C# where word boundary \b doesn't work well at end
        if term in ["C++", "C#", "C"]:
            if term == "C++":
                escaped.append(r"(?:(?<=\s)|(?<=^)|(?<=[(\[,]))c\+\+(?=[)\],.\s]|$)")
            elif term == "C#":
                escaped.append(r"(?:(?<=\s)|(?<=^)|(?<=[(\[,]))c\#(?=[)\],.\s]|$)")
            elif term == "C":
                escaped.append(r"(?:(?<=\s)|(?<=^)|(?<=[(\[,]))c(?=[)\],.\s]|$)")
        else:
            escaped.append(r"\b" + esc + r"\b")
    pattern_str = "|".join(escaped)
    return re.compile(pattern_str, re.IGNORECASE)


COMPILED_SKILL_PATTERNS = {
    skill: _build_search_regex(skill, data["aliases"])
    for skill, data in SKILL_TAXONOMY.items()
}


def extract_skills_from_text(text: str) -> Dict[str, Dict[str, Any]]:
    """Extract known skills from text using ontology patterns.
    Returns dictionary: {canonical_name: {"category": str, "occurrences": int}}
    """
    if not text:
        return {}
    
    found_skills = {}
    for skill, pattern in COMPILED_SKILL_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            found_skills[skill] = {
                "name": skill,
                "category": SKILL_TAXONOMY[skill]["category"],
                "count": len(matches)
            }
    return found_skills


def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Compute cosine similarity between Resume and Job Description using TF-IDF."""
    if not resume_text or not jd_text:
        return 0.0
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(sim) * 100, 1)
    except Exception:
        return 50.0


def calculate_ats_score(resume_text: str, jd_text: str, matching_skills_count: int, total_jd_skills: int) -> Dict[str, Any]:
    """Evaluate resume against typical Applicant Tracking System (ATS) criteria."""
    checks = []
    score = 70.0 # base
    
    # 1. Word count check
    word_count = len(resume_text.split())
    if 350 <= word_count <= 950:
        score += 10
        checks.append({"name": "Resume Length", "status": "pass", "detail": f"{word_count} words (Optimal for 1-2 pages)"})
    elif word_count < 300:
        score -= 10
        checks.append({"name": "Resume Length", "status": "warn", "detail": f"{word_count} words (Too brief, add more project/experience details)"})
    else:
        checks.append({"name": "Resume Length", "status": "pass", "detail": f"{word_count} words"})

    # 2. Measurable metrics check (percentages, numbers, dollar/rupee signs, improvements)
    metric_matches = re.findall(r"\b(?:\d{1,3}%|\d+\+? (?:users|clients|transactions|ms|seconds|hours|queries)|reduced by \d+|improved by \d+|increased by \d+)\b", resume_text, re.I)
    if len(metric_matches) >= 3:
        score += 10
        checks.append({"name": "Quantifiable Achievements", "status": "pass", "detail": f"Found {len(metric_matches)} quantified impacts (e.g., metrics, percentages)"})
    else:
        score -= 5
        checks.append({"name": "Quantifiable Achievements", "status": "warn", "detail": "Few quantified impact metrics found. Use numbers to prove project outcomes."})

    # 3. Action verbs
    action_verbs = ["developed", "implemented", "designed", "architected", "optimized", "built", "spearheaded", "integrated", "reduced", "increased"]
    found_verbs = [v for v in action_verbs if re.search(r"\b" + v + r"\b", resume_text, re.I)]
    if len(found_verbs) >= 5:
        score += 5
        checks.append({"name": "Impact Action Verbs", "status": "pass", "detail": f"Strong action verb presence: {', '.join(found_verbs[:4])}..."})
    else:
        checks.append({"name": "Impact Action Verbs", "status": "warn", "detail": "Use more strong action verbs at the start of bullet points."})

    # 4. Keyword Match Ratio
    if total_jd_skills > 0:
        ratio = matching_skills_count / total_jd_skills
        if ratio >= 0.7:
            score += 10
            checks.append({"name": "JD Keyword Density", "status": "pass", "detail": f"{int(ratio*100)}% of JD core technical keywords matched"})
        elif ratio >= 0.4:
            score += 5
            checks.append({"name": "JD Keyword Density", "status": "pass", "detail": f"{int(ratio*100)}% of JD keywords matched"})
        else:
            score -= 10
            checks.append({"name": "JD Keyword Density", "status": "fail", "detail": f"Only {int(ratio*100)}% of JD keywords present. Significant keyword gap."})

    final_score = max(35, min(98, round(score)))
    return {
        "score": final_score,
        "grade": "A+" if final_score >= 88 else ("A" if final_score >= 78 else ("B" if final_score >= 65 else "C")),
        "checks": checks
    }


def analyze_skill_gaps(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Main analysis engine: extracts skills, categorizes gaps, and calculates multi-dimensional scores."""
    resume_skills_map = extract_skills_from_text(resume_text)
    jd_skills_map = extract_skills_from_text(jd_text)
    
    resume_skills_set = set(resume_skills_map.keys())
    jd_skills_set = set(jd_skills_map.keys())
    
    matching_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
    missing_skills = sorted(list(jd_skills_set - resume_skills_set))
    bonus_skills = sorted(list(resume_skills_set - jd_skills_set))
    
    # Calculate dimensional scores
    total_jd = len(jd_skills_set) if jd_skills_set else 1
    skills_fit = round((len(matching_skills) / total_jd) * 100, 1)
    skills_fit = min(100.0, skills_fit)
    
    semantic_sim = compute_semantic_similarity(resume_text, jd_text)
    
    # Experience heuristics (look for year mentions)
    exp_matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|year)\s*(?:of\s*)?experience", jd_text, re.I)
    jd_exp_req = int(exp_matches[0]) if exp_matches else 1
    
    resume_exp_matches = re.findall(r"(\d+)\+?\s*(?:years|yrs|year)\s*(?:of\s*)?experience", resume_text, re.I)
    cand_exp = int(resume_exp_matches[0]) if resume_exp_matches else (0 if "fresher" in resume_text.lower() or "graduate" in resume_text.lower() else 1)
    
    if cand_exp >= jd_exp_req:
        experience_fit = 95.0
    elif cand_exp == 0 and jd_exp_req <= 1:
        experience_fit = 85.0
    else:
        diff = max(0, jd_exp_req - cand_exp)
        experience_fit = max(40.0, round(90.0 - (diff * 20.0), 1))
        
    # Project match heuristics
    project_sim = compute_semantic_similarity(
        resume_text.split("PROJECTS")[-1] if "PROJECTS" in resume_text else resume_text,
        jd_text
    )
    project_fit = min(98.0, max(45.0, round(project_sim * 1.4, 1)))

    # Weighted Overall Score
    # Skills: 45%, Semantic: 25%, Project Relevance: 15%, Experience: 15%
    overall_score = round(
        (skills_fit * 0.45) + (semantic_sim * 0.25) + (project_fit * 0.15) + (experience_fit * 0.15)
    )
    overall_score = max(25, min(98, overall_score))
    
    # ATS analysis
    ats_data = calculate_ats_score(resume_text, jd_text, len(matching_skills), len(jd_skills_set))
    
    # Skill category breakdown for radar chart
    categories = ["Languages", "Frontend", "Backend", "Database", "Cloud & DevOps", "Core CS", "Testing & Tools", "AI & Data"]
    category_radar = []
    for cat in categories:
        cat_jd = [s for s in jd_skills_set if SKILL_TAXONOMY.get(s, {}).get("category") == cat]
        cat_match = [s for s in matching_skills if SKILL_TAXONOMY.get(s, {}).get("category") == cat]
        req_count = len(cat_jd)
        match_count = len(cat_match)
        match_pct = round((match_count / req_count * 100)) if req_count > 0 else (100 if [s for s in resume_skills_set if SKILL_TAXONOMY.get(s, {}).get("category") == cat] else 0)
        category_radar.append({
            "category": cat,
            "required": req_count,
            "matched": match_count,
            "score": match_pct
        })

    # Prioritize missing skills into High, Medium, Low priority
    missing_skill_details = []
    for sk in missing_skills:
        cat = SKILL_TAXONOMY.get(sk, {}).get("category", "General")
        # If mentioned multiple times in JD, higher priority
        count = jd_skills_map.get(sk, {}).get("count", 1)
        priority = "High" if count >= 2 or cat in ["Languages", "Backend", "Frontend"] else "Medium"
        missing_skill_details.append({
            "name": sk,
            "category": cat,
            "priority": priority,
            "importance": f"Mentioned {count} time(s) in JD requirements"
        })

    return {
        "overall_score": overall_score,
        "skills_score": skills_fit,
        "semantic_score": semantic_sim,
        "experience_score": experience_fit,
        "project_score": project_fit,
        "ats_score": ats_data["score"],
        "ats_grade": ats_data["grade"],
        "ats_checks": ats_data["checks"],
        "matching_skills": [
            {"name": s, "category": SKILL_TAXONOMY.get(s, {}).get("category", "General")}
            for s in matching_skills
        ],
        "missing_skills": missing_skill_details,
        "bonus_skills": [
            {"name": s, "category": SKILL_TAXONOMY.get(s, {}).get("category", "General")}
            for s in bonus_skills[:12]
        ],
        "category_radar": category_radar,
        "summary": {
            "total_jd_skills": len(jd_skills_set),
            "matched_count": len(matching_skills),
            "missing_count": len(missing_skills),
            "bonus_count": len(bonus_skills)
        }
    }


if __name__ == "__main__":
    from backend.sample_data import SAMPLE_RESUMES, SAMPLE_JDS
    resume = SAMPLE_RESUMES["sde_fresher"]["text"]
    jd = SAMPLE_JDS["google_sde"]["text"]
    analysis = analyze_skill_gaps(resume, jd)
    print("Match Score:", analysis["overall_score"])
    print("Matching Skills:", [s["name"] for s in analysis["matching_skills"]])
    print("Missing Skills:", [s["name"] for s in analysis["missing_skills"]])
    print("ATS Score:", analysis["ats_score"])
    print("Matcher test successful!")
