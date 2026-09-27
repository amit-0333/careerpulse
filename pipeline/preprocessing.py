import re
from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine
from pipeline.skills import SKILLS_LIST


TECH_JOB_KEYWORDS = [
    # Core tech roles
    "data scientist", "data engineer", "data analyst",
    "machine learning", "ml engineer", "ai engineer",
    "software engineer", "software developer",
    "backend engineer", "frontend engineer", "fullstack",
    "devops engineer", "cloud engineer", "platform engineer",
    "python developer", "java developer", "javascript developer",
    "nlp engineer", "research scientist", "research engineer",
    "data science", "deep learning", "computer vision",
    "business intelligence", "bi developer", "bi analyst",
    "database administrator", "data architect",
    "cybersecurity", "security engineer", "security analyst",
    "web developer", "mobile developer", "android developer",
    "ios developer", "react developer", "node developer",
    "qa engineer", "quality assurance engineer",
    "product manager", "technical product manager",
    "data manager", "analytics engineer", "etl developer",
    "big data", "spark engineer", "hadoop engineer",

    # Additional tech roles
    "analyst", "developer", "engineer", "architect",
    "data consultant", "tech consultant", "it consultant",
    "head of data", "head of engineering", "vp engineering",
    "chief data", "chief technology", "cto", "cdo",
    "site reliability", "infrastructure engineer",
    "blockchain developer", "smart contract",
    "embedded engineer", "firmware engineer",
    "network engineer", "systems engineer",
    "solutions architect", "cloud architect",
    "data lead", "tech lead", "engineering lead",
    "ml ops", "mlops", "dataops", "data ops",
    "quantitative analyst", "quant developer",
    "computer scientist", "ai researcher",
    "llm engineer", "prompt engineer",
    "data intern", "software intern", "ml intern",
    "junior developer", "junior engineer",
    "senior developer", "senior engineer",
    "staff engineer", "principal engineer",
]

JOB_TYPE_MAP = {
    "full_time": "full_time",
    "fulltime": "full_time",
    "full-time": "full_time",
    "permanent": "full_time",
    "part_time": "part_time",
    "parttime": "part_time",
    "part-time": "part_time",
    "contract": "contract",
    "contractor": "contract",
    "internship": "internship",
    "intern": "internship",
    "remote": "remote",
    "hybrid": "hybrid",
    "onsite": "onsite",
    "on-site": "onsite",
}

def remove_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_skills(text):
    if not text:
        return ""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_LIST:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return ", ".join(found_skills)

def is_tech_job(title):
    title_lower = title.lower()
    return any(re.search(r'\b' + re.escape(k) + r'\b', title_lower) for k in TECH_JOB_KEYWORDS)

def standardize_job_type(job_type):
    if not job_type:
        return "unknown"
    return JOB_TYPE_MAP.get(job_type.lower().strip(), job_type.lower().strip())

def clean_text(text):
    if not text:
        return ""
    text = remove_html(text)
    text = re.sub(r"[^\w\s.,!?-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def preprocess_jobs():
    print(f"[INFO] Starting preprocessing...")
    with Session(engine) as session:
        jobs = session.query(Job).all()
        print(f"[INFO] Total jobs to process: {len(jobs)}")
        updated = 0
        deleted = 0
        for job in jobs:
            if not is_tech_job(job.title):
                session.delete(job)
                deleted += 1
                continue
            clean_desc = clean_text(job.description)
            skills = extract_skills(f"{clean_desc} {job.tags} {job.title}")
            job_type = standardize_job_type(job.job_type)
            job.description = clean_desc
            job.tags = skills if skills else job.tags
            job.job_type = job_type
            updated += 1
            if updated % 100 == 0:
                print(f"[INFO] Processed {updated} jobs...")
        session.commit()
        print(f"[SUCCESS] Cleaned: {updated} tech jobs kept")
        print(f"[INFO] Removed: {deleted} non-tech jobs")

if __name__ == "__main__":
    preprocess_jobs()