from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from pipeline.ingestion import Job

engine = create_engine("sqlite:///data/database/careerpulse.db")

def show_summary():
    with Session(engine) as session:
        total = session.query(Job).count()
        remoteok = session.query(Job).filter_by(source="remoteok").count()
        arbeitnow = session.query(Job).filter_by(source="arbeitnow").count()
        muse = session.query(Job).filter_by(source="themuse").count()
        adzuna = session.query(Job).filter_by(source="adzuna").count()
        print(f"[DB] Total jobs:    {total}")
        print(f"[DB] RemoteOK:      {remoteok}")
        print(f"[DB] Arbeitnow:     {arbeitnow}")
        print(f"[DB] The Muse:      {muse}")
        print(f"[DB] Adzuna:        {adzuna}")

def show_sample(source=None, limit=5):
    with Session(engine) as session:
        query = session.query(Job)
        if source:
            query = query.filter_by(source=source)
        jobs = query.limit(limit).all()
        for job in jobs:
            print(f"[JOB] -------------------------")
            print(f"  Title:    {job.title}")
            print(f"  Company:  {job.company}")
            print(f"  Location: {job.location}")
            print(f"  Type:     {job.job_type}")
            print(f"  Tags:     {job.tags}")
            print(f"  Salary:   {job.salary_min} - {job.salary_max}")
            print(f"  Source:   {job.source}")
            print(f"  Posted:   {job.date_posted}")
            print(f"  URL:      {job.apply_url}")

def search_jobs(keyword):
    with Session(engine) as session:
        jobs = session.query(Job).filter(
            Job.title.contains(keyword)
        ).limit(10).all()
        print(f"[SEARCH] Results for: {keyword}")
        for job in jobs:
            print(f"  {job.title} | {job.company} | {job.location} | {job.source}")

def show_by_type(job_type):
    with Session(engine) as session:
        jobs = session.query(Job).filter_by(job_type=job_type).limit(10).all()
        print(f"[FILTER] Job type: {job_type}")
        for job in jobs:
            print(f"  {job.title} | {job.company} | {job.location}")

if __name__ == "__main__":
    print("[INFO] CareerPulse Database Viewer")
    print("[INFO] Summary:")
    show_summary()

    print("\n[INFO] Sample RemoteOK jobs:")
    show_sample(source="remoteok", limit=3)

    print("\n[INFO] Sample Adzuna jobs:")
    show_sample(source="adzuna", limit=3)

    print("\n[INFO] Search: python jobs")
    search_jobs("python")

    print("\n[INFO] Search: data science jobs")
    search_jobs("data")

    print("\n[INFO] Remote jobs:")
    show_by_type("remote")