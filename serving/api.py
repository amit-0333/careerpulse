import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pipeline.location import location_matches
os.makedirs("data/database", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/feature_store", exist_ok=True)
os.makedirs("data/mlflow", exist_ok=True)

from pipeline.ingestion import Base, engine
Base.metadata.create_all(engine)

from model.llm_coach import analyze_career, generate_cover_letter, get_interview_questions
from model.resume_parser import parse_resume

app = FastAPI(
    title="CareerPulse API",
    description="AI powered career assistant API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("[INFO] API Starting up...")
    print("[INFO] Database initialized")

class CareerRequest(BaseModel):
    target_role: str
    current_skills: str
    experience_years: int

class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    user_skills: str
    experience_years: int

class InterviewRequest(BaseModel):
    job_title: str
    user_skills: str

@app.get("/")
def root():
    return {
        "name": "CareerPulse API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
def analyze(request: CareerRequest):
    print(f"[API] Analyze request: {request.target_role}")
    response, jobs = analyze_career(
        target_role=request.target_role,
        current_skills=request.current_skills,
        experience_years=request.experience_years
    )
    return {
        "status": "success",
        "target_role": request.target_role,
        "llm_analysis": response,
        "matching_jobs": jobs[:10],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...)
):
    print(f"[API] Resume upload: {file.filename}")
    temp_path = f"data/raw/temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    resume_data = parse_resume(temp_path)
    os.remove(temp_path)
    response, jobs = analyze_career(
        target_role=target_role,
        current_skills=resume_data["skills_str"],
        experience_years=resume_data["experience_years"]
    )
    return {
        "status": "success",
        "resume_data": {
            "name": resume_data["name"],
            "email": resume_data["email"],
            "skills": resume_data["skills"],
            "experience_years": resume_data["experience_years"],
            "education": resume_data["education"],
        },
        "target_role": target_role,
        "llm_analysis": response,
        "matching_jobs": jobs[:10],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/cover-letter")
def cover_letter(request: CoverLetterRequest):
    print(f"[API] Cover letter: {request.job_title} at {request.company}")
    letter = generate_cover_letter(
        job_title=request.job_title,
        company=request.company,
        user_skills=request.user_skills,
        experience_years=request.experience_years
    )
    return {
        "status": "success",
        "cover_letter": letter,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/interview-prep")
def interview_prep(request: InterviewRequest):
    print(f"[API] Interview prep: {request.job_title}")
    questions = get_interview_questions(
        job_title=request.job_title,
        user_skills=request.user_skills
    )
    return {
        "status": "success",
        "interview_questions": questions,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/jobs")
def get_jobs(limit: int = 10, source: str = None, location: str = None, include_remote: bool = True):
    from sqlalchemy.orm import Session
    from pipeline.ingestion import Job, engine
    with Session(engine) as session:
        query = session.query(Job)
        if source:
            query = query.filter_by(source=source)
        jobs = query.all()
        if location:
            jobs = [
                j for j in jobs
                if location_matches(j.location, location, j.job_type, include_remote)
            ]
        jobs = jobs[:limit]
        return {
            "status": "success",
            "total": len(jobs),
            "jobs": [
                {
                    "title": j.title,
                    "company": j.company,
                    "location": j.location,
                    "job_type": j.job_type,
                    "tags": j.tags,
                    "apply_url": j.apply_url,
                }
                for j in jobs
            ]
        }

@app.get("/stats")
def stats():
    from sqlalchemy.orm import Session
    from pipeline.ingestion import Job, engine
    with Session(engine) as session:
        total = session.query(Job).count()
        remoteok = session.query(Job).filter_by(source="remoteok").count()
        arbeitnow = session.query(Job).filter_by(source="arbeitnow").count()
        muse = session.query(Job).filter_by(source="themuse").count()
        adzuna = session.query(Job).filter_by(source="adzuna").count()
        return {
            "status": "success",
            "total_jobs": total,
            "by_source": {
                "remoteok": remoteok,
                "arbeitnow": arbeitnow,
                "themuse": muse,
                "adzuna": adzuna,
            },
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("serving.api:app", host="0.0.0.0", port=port, reload=False)