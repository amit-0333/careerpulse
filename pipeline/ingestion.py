import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text
from sqlalchemy.orm import declarative_base, Session

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
MUSE_API_KEY = os.getenv("MUSE_API_KEY")

Base = declarative_base()
engine = create_engine("sqlite:///data/database/careerpulse.db")

RELEVANT_KEYWORDS = [
    "data", "machine learning", "ml", "ai", "python", "analyst",
    "engineer", "developer", "software", "backend", "frontend",
    "fullstack", "devops", "cloud", "nlp", "deep learning",
    "statistics", "database", "sql", "java", "javascript",
    "react", "node", "django", "flask", "tensorflow", "pytorch",
    "computer science", "it", "tech", "cyber", "security",
    "product manager", "scrum", "agile", "research", "scientist"
]

def is_relevant_job(title, tags="", description=""):
    combined = f"{title} {tags} {description}".lower()
    return any(keyword.lower() in combined for keyword in RELEVANT_KEYWORDS)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True)
    title = Column(String)
    company = Column(String)
    description = Column(Text)
    location = Column(String)
    job_type = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    tags = Column(String)
    source = Column(String)
    apply_url = Column(String)
    date_posted = Column(String)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)

def save_jobs(jobs):
    saved = 0
    skipped = 0
    with Session(engine) as session:
        for job in jobs:
            existing = session.query(Job).filter_by(job_id=job["job_id"]).first()
            if not existing:
                session.add(Job(**job))
                saved += 1
            else:
                skipped += 1
        session.commit()
    print(f"[DB] Saved: {saved} new jobs | Skipped: {skipped} duplicates")

def fetch_remoteok():
    print("[API] Fetching RemoteOK jobs...")
    try:
        url = "https://remoteok.com/api"
        headers = {"User-Agent": "careerpulse-app"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[WARNING] RemoteOK failed: {response.status_code}")
            return []
        raw = response.json()[1:]
    except Exception as e:
        print(f"[ERROR] RemoteOK error: {e}")
        return []
    jobs = []
    for j in raw:
        title = j.get("position", "")
        tags = ", ".join(j.get("tags", []))
        description = j.get("description", "")
        if not is_relevant_job(title, tags, description):
            continue
        jobs.append({
            "job_id": f"remoteok_{j.get('id', '')}",
            "title": title,
            "company": j.get("company", ""),
            "description": description,
            "location": j.get("location", "Remote"),
            "job_type": "remote",
            "salary_min": float(j.get("salary_min", 0) or 0),
            "salary_max": float(j.get("salary_max", 0) or 0),
            "tags": tags,
            "source": "remoteok",
            "apply_url": j.get("apply_url", ""),
            "date_posted": j.get("date", ""),
        })
    print(f"[SUCCESS] RemoteOK: {len(jobs)} jobs fetched")
    return jobs

def fetch_arbeitnow():
    print("[API] Fetching Arbeitnow jobs...")
    jobs = []
    for page in range(1, 6):
        try:
            url = f"https://arbeitnow.com/api/job-board-api?page={page}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[WARNING] Arbeitnow page {page} failed: {response.status_code}")
                continue
            data = response.json()
        except Exception as e:
            print(f"[ERROR] Arbeitnow page {page} error: {e}")
            continue
        for j in data.get("data", []):
            title = j.get("title", "")
            tags = ", ".join(j.get("tags", []))
            description = j.get("description", "")
            if not is_relevant_job(title, tags, description):
                continue
            jobs.append({
                "job_id": f"arbeitnow_{j.get('slug', '')}",
                "title": title,
                "company": j.get("company_name", ""),
                "description": description,
                "location": j.get("location", ""),
                "job_type": "remote" if j.get("remote") else "onsite",
                "salary_min": 0.0,
                "salary_max": 0.0,
                "tags": tags,
                "source": "arbeitnow",
                "apply_url": j.get("url", ""),
                "date_posted": str(j.get("created_at", "")),
            })
    print(f"[SUCCESS] Arbeitnow: {len(jobs)} jobs fetched")
    return jobs

def fetch_themuse():
    print("[API] Fetching The Muse jobs...")
    jobs = []
    for page in range(1, 6):
        try:
            url = f"https://www.themuse.com/api/public/jobs?api_key={MUSE_API_KEY}&page={page}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[WARNING] The Muse page {page} failed: {response.status_code}")
                continue
            data = response.json()
        except Exception as e:
            print(f"[ERROR] The Muse page {page} error: {e}")
            continue
        for j in data.get("results", []):
            title = j.get("name", "")
            tags = ", ".join([c.get("name", "") for c in j.get("categories", [])])
            description = j.get("contents", "")
            if not is_relevant_job(title, tags, description):
                continue
            locations = j.get("locations", [])
            location = locations[0].get("name", "") if locations else ""
            jobs.append({
                "job_id": f"muse_{j.get('id', '')}",
                "title": title,
                "company": j.get("company", {}).get("name", ""),
                "description": description,
                "location": location,
                "job_type": j.get("type", ""),
                "salary_min": 0.0,
                "salary_max": 0.0,
                "tags": tags,
                "source": "themuse",
                "apply_url": j.get("refs", {}).get("landing_page", ""),
                "date_posted": j.get("publication_date", ""),
            })
    print(f"[SUCCESS] The Muse: {len(jobs)} jobs fetched")
    return jobs

def fetch_adzuna():
    print("[API] Fetching Adzuna jobs...")
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[WARNING] Adzuna keys not found, skipping...")
        return []
    jobs = []
    for page in range(1, 6):
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_APP_KEY}&results_per_page=50"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"[WARNING] Adzuna page {page} failed: {response.status_code}")
                continue
            data = response.json()
            for j in data.get("results", []):
                title = j.get("title", "")
                tags = j.get("category", {}).get("label", "")
                description = j.get("description", "")
                if not is_relevant_job(title):
                    continue
                jobs.append({
                    "job_id": f"adzuna_{j.get('id', '')}",
                    "title": title,
                    "company": j.get("company", {}).get("display_name", ""),
                    "description": description,
                    "location": j.get("location", {}).get("display_name", ""),
                    "job_type": j.get("contract_time", ""),
                    "salary_min": float(j.get("salary_min", 0) or 0),
                    "salary_max": float(j.get("salary_max", 0) or 0),
                    "tags": tags,
                    "source": "adzuna",
                    "apply_url": j.get("redirect_url", ""),
                    "date_posted": j.get("created", ""),
                })
        except Exception as e:
            print(f"[ERROR] Adzuna page {page} error: {e}")
            continue
    print(f"[SUCCESS] Adzuna: {len(jobs)} jobs fetched")
    return jobs

def update_last_updated():
    os.makedirs("data", exist_ok=True)
    with open("data/last_updated.txt", "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    print(f"[INFO] CareerPulse Ingestion Started: {datetime.now()}")
    all_jobs = []
    all_jobs.extend(fetch_remoteok())
    all_jobs.extend(fetch_arbeitnow())
    all_jobs.extend(fetch_themuse())
    all_jobs.extend(fetch_adzuna())
    print(f"[INFO] Total fetched: {len(all_jobs)}")
    save_jobs(all_jobs)
    update_last_updated()
    print(f"[INFO] Ingestion completed: {datetime.now()}")