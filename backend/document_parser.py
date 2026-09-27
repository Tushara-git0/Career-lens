"""Document Parser for CareerLens AI.
Supports PDF (pypdf), DOCX (python-docx), and raw text.
Performs clean extraction and structured section segmentation.
"""

import io
import re
from typing import Dict, List, Any, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


SECTION_HEADERS = {
    "education": [
        "education", "academic background", "qualifications", "academics",
        "educational qualifications", "academic details"
    ],
    "skills": [
        "technical skills", "skills", "skills & tools", "core competencies",
        "technologies", "tech stack", "tools & technologies", "skills summary"
    ],
    "experience": [
        "work experience", "experience", "professional experience",
        "employment history", "internships", "internship experience",
        "work history", "industrial experience"
    ],
    "projects": [
        "projects", "academic projects", "key projects", "personal projects",
        "technical projects", "featured projects"
    ],
    "certifications": [
        "certifications", "certificates", "licenses & certifications",
        "courses & certifications", "achievements", "honors & awards",
        "awards & achievements"
    ],
    "summary": [
        "summary", "professional summary", "objective", "career objective",
        "profile", "about me"
    ]
}


def clean_text(raw_text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if not raw_text:
        return ""
    # Normalize windows/unix line endings
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove control characters except newlines/tabs
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Collapse multiple consecutive blank lines into at most 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes using pypdf."""
    if not pypdf:
        raise RuntimeError("pypdf is not installed.")
    
    stream = io.BytesIO(file_bytes)
    reader = pypdf.PdfReader(stream)
    pages_text = []
    
    for i, page in enumerate(reader.pages):
        page_content = page.extract_text() or ""
        if page_content.strip():
            pages_text.append(page_content)
            
    return clean_text("\n\n".join(pages_text))


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract raw text from DOCX bytes using python-docx."""
    if not docx:
        raise RuntimeError("python-docx is not installed.")
    
    stream = io.BytesIO(file_bytes)
    doc = docx.Document(stream)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # Also extract text inside tables if any
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)
                
    return clean_text("\n".join(paragraphs))


def parse_resume_document(filename: str, file_bytes: bytes) -> str:
    """Extract text from PDF, DOCX, or plain text based on file extension."""
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith((".docx", ".doc")):
        return extract_text_from_docx(file_bytes)
    elif lower_name.endswith((".txt", ".md")):
        return clean_text(file_bytes.decode("utf-8", errors="replace"))
    else:
        # Attempt PDF first, then utf-8 text
        try:
            return extract_text_from_pdf(file_bytes)
        except Exception:
            return clean_text(file_bytes.decode("utf-8", errors="replace"))


def segment_sections(text: str) -> Dict[str, str]:
    """Segment a resume into structured sections based on standard headings."""
    lines = text.split("\n")
    sections: Dict[str, List[str]] = {
        "header": [],
        "summary": [],
        "education": [],
        "skills": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "other": []
    }
    
    current_section = "header"
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Check if this line looks like a section header
        # Usually short, upper case or title case, or with colon
        clean_header = re.sub(r"[:\-_=~*#]", "", stripped).strip().lower()
        
        detected = None
        if len(clean_header) <= 35:
            for sec_name, keywords in SECTION_HEADERS.items():
                if any(clean_header == kw or clean_header.startswith(kw + " ") or clean_header.endswith(" " + kw) for kw in keywords):
                    detected = sec_name
                    break
        
        if detected:
            current_section = detected
        else:
            sections[current_section].append(stripped)
            
    return {sec: "\n".join(content) for sec, content in sections.items() if content}


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract email, phone, and profile links from text."""
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5}", text)
    linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", text, re.I)
    github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", text, re.I)
    
    # Try extracting candidate name from top line
    first_lines = [l.strip() for l in text.split("\n") if l.strip()]
    candidate_name = None
    if first_lines:
        top_line = first_lines[0]
        # Ignore if it has @ or http or digits
        if not any(char in top_line for char in ["@", "http", ".com", "/", "\\", "+"]) and len(top_line.split()) <= 4:
            candidate_name = top_line
            
    return {
        "name": candidate_name or "Candidate",
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None
    }


if __name__ == "__main__":
    from backend.sample_data import SAMPLE_RESUMES
    sample_sde = SAMPLE_RESUMES["sde_fresher"]["text"]
    segmented = segment_sections(sample_sde)
    contacts = extract_contact_info(sample_sde)
    print("Contact info:", contacts)
    print("Detected sections:", list(segmented.keys()))
    print("Parser successfully tested!")
