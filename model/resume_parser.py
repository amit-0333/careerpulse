import os
import re
import pymupdf as fitz
from dotenv import load_dotenv
from pipeline.skills import SKILLS_LIST

load_dotenv()



EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*years?\s*of\s*experience',
    r'(\d+)\+?\s*yrs?\s*of\s*experience',
    r'experience\s*of\s*(\d+)\+?\s*years?',
    r'(\d+)\+?\s*years?\s*experience',
]

EDUCATION_KEYWORDS = [
    "b.tech", "b.e", "bachelor", "b.sc", "bsc",
    "m.tech", "m.e", "master", "m.sc", "msc",
    "phd", "doctorate", "mba", "diploma",
    "computer science", "information technology",
    "electronics", "electrical", "mechanical",
]

def extract_text_from_pdf(pdf_path):
    print(f"[INFO] Extracting text from: {pdf_path}")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    print(f"[SUCCESS] Extracted {len(text)} characters from PDF")
    return text

def extract_skills(text):
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_LIST:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return found_skills

def extract_experience(text):
    text_lower = text.lower()
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))
    if "fresher" in text_lower or "fresh graduate" in text_lower:
        return 0
    if "intern" in text_lower:
        return 0
    return 1

def extract_education(text):
    text_lower = text.lower()
    found = []
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)
    return found

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 2 and len(line) < 50:
            if not any(char.isdigit() for char in line):
                if not any(kw in line.lower() for kw in ["resume", "cv", "curriculum", "email", "phone"]):
                    return line
    return "Unknown"

def extract_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not found"

def parse_resume(pdf_path):
    print(f"[INFO] Parsing resume: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    experience = extract_experience(text)
    education = extract_education(text)
    result = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "skills_str": ", ".join(skills),
        "experience_years": experience,
        "education": education,
        "raw_text": text,
    }
    print(f"[SUCCESS] Resume parsed successfully")
    print(f"[INFO] Name:       {name}")
    print(f"[INFO] Email:      {email}")
    print(f"[INFO] Phone:      {phone}")
    print(f"[INFO] Experience: {experience} years")
    print(f"[INFO] Skills:     {', '.join(skills)}")
    print(f"[INFO] Education:  {', '.join(education)}")
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "test_resume.pdf"
    if not os.path.exists(pdf_path):
        print("[WARNING] No PDF found, creating test resume data...")
        test_data = {
            "name": "Amit Kumar",
            "email": "amit@email.com",
            "phone": "9876543210",
            "skills": ["python", "pandas", "scikit-learn", "sql", "git"],
            "skills_str": "python, pandas, scikit-learn, sql, git",
            "experience_years": 1,
            "education": ["b.tech", "computer science"],
            "raw_text": "Test resume text",
        }
        print(f"[INFO] Test profile created:")
        print(f"  Name:   {test_data['name']}")
        print(f"  Skills: {test_data['skills_str']}")
        print(f"  Exp:    {test_data['experience_years']} years")

        from model.llm_coach import analyze_career
        print("\n[INFO] Running career analysis with test profile...")
        response, jobs = analyze_career(
            target_role="Data Scientist",
            current_skills=test_data["skills_str"],
            experience_years=test_data["experience_years"]
        )
        print("\n[LLM CAREER COACH RESPONSE]")
        print(response)
    else:
        result = parse_resume(pdf_path)
        from model.llm_coach import analyze_career
        print("\n[INFO] Running career analysis...")
        response, jobs = analyze_career(
            target_role="Data Scientist",
            current_skills=result["skills_str"],
            experience_years=result["experience_years"]
        )
        print("\n[LLM CAREER COACH RESPONSE]")
        print(response)