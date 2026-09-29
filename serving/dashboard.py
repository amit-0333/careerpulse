import streamlit as st
import requests
import tempfile
import os
from datetime import datetime
from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine
import pickle

API_URL = os.getenv("http://localhost:8000", "https://your-render-url.onrender.com")

st.set_page_config(
    page_title="CareerPulse",
    page_icon="CP",
    layout="wide"
)

st.title("CareerPulse")
st.caption("AI Powered Career Assistant")

page = st.sidebar.selectbox(
    "Navigation",
    ["Resume Analyzer", "Job Browser", "Cover Letter", "Interview Prep"]
)

def clean_html(text):
    return text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

def get_sidebar_stats():
    try:
        with Session(engine) as session:
            total = session.query(Job).count()
            remote = session.query(Job).filter_by(job_type="remote").count()
            top_skill_row = session.query(Job.tags).filter(Job.tags != None).limit(100).all()
            skill_counts = {}
            for row in top_skill_row:
                if row[0]:
                    for skill in row[0].split(","):
                        skill = skill.strip().lower()
                        if skill:
                            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            top_skill = max(skill_counts, key=skill_counts.get) if skill_counts else "python"
            try:
                with open("data/feature_store/model_metrics.pkl", "rb") as f:
                    metrics = pickle.load(f)
                accuracy = round(metrics.get("accuracy", 0) * 100, 1)
            except:
                accuracy = 0
            try:
                with open("data/last_updated.txt", "r") as f:
                    last_trained = f.read().strip()[:10]
            except:
                last_trained = "unknown"
            return {
                "total": total,
                "remote": remote,
                "top_skill": top_skill,
                "accuracy": accuracy,
                "last_trained": last_trained,
            }
    except:
        return None

with st.sidebar:
    st.divider()
    st.caption("System Stats")
    stats = get_sidebar_stats()
    if stats:
        st.metric("Total Jobs", stats["total"])
        st.metric("Remote Jobs", stats["remote"])
        st.metric("Top Skill", stats["top_skill"].title())
        st.metric("Model Accuracy", f"{stats['accuracy']}%")
        st.metric("Last Updated", stats["last_trained"])
    else:
        st.caption("[WARNING] Stats unavailable")

if page == "Resume Analyzer":
    st.header("Resume Analyzer")
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
        target_role = st.text_input("Target Role", placeholder="e.g. ML Engineer")
        experience = st.number_input("Years of Experience", min_value=0, max_value=30, value=1)

    with col2:
        manual_skills = st.text_area(
            "Or enter skills manually (comma separated)",
            placeholder="python, sql, pandas, git"
        )

    if st.button("Analyze My Profile"):
        if not target_role:
            st.error("[ERROR] Please enter a target role")
        elif uploaded_file:
            with st.spinner("Parsing resume and analyzing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                with open(tmp_path, "rb") as f:
                    response = requests.post(
                        f"{API_URL}/upload-resume",
                        files={"file": (uploaded_file.name, f, "application/pdf")},
                        data={"target_role": target_role}
                    )
                os.unlink(tmp_path)
                if response.status_code == 200:
                    data = response.json()
                    resume_data = data["resume_data"]
                    st.subheader("Skills Found in Your Resume")
                    st.write(", ".join(resume_data["skills"]))
                    st.subheader("Career Analysis")
                    st.markdown(clean_html(data["llm_analysis"]))
                    st.subheader("Top Matching Jobs")
                    for job in data["matching_jobs"][:5]:
                        with st.expander(f"{job['match_pct']}% | {job['title']} at {job['company']}"):
                            st.write(f"Location: {job['location']}")
                            st.write(f"Type: {job['job_type']}")
                            st.write(f"Matched Skills: {', '.join(job['matched_skills'])}")
                            st.write(f"Missing Skills: {', '.join(job['missing_skills'])}")
                            if job['apply_url']:
                                st.link_button("Apply Now", job['apply_url'])
                else:
                    st.error(f"[ERROR] API error: {response.status_code}")
        elif manual_skills:
            with st.spinner("Analyzing your skills..."):
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={
                        "target_role": target_role,
                        "current_skills": manual_skills,
                        "experience_years": experience
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Career Analysis")
                    st.markdown(clean_html(data["llm_analysis"]))
                    st.subheader("Top Matching Jobs")
                    for job in data["matching_jobs"][:5]:
                        with st.expander(f"{job['match_pct']}% | {job['title']} at {job['company']}"):
                            st.write(f"Location: {job['location']}")
                            st.write(f"Type: {job['job_type']}")
                            st.write(f"Matched Skills: {', '.join(job['matched_skills'])}")
                            st.write(f"Missing Skills: {', '.join(job['missing_skills'])}")
                            if job['apply_url']:
                                st.link_button("Apply Now", job['apply_url'])
                else:
                    st.error(f"[ERROR] API error: {response.status_code}")
        else:
            st.error("[ERROR] Please upload a resume or enter skills manually")

elif page == "Job Browser":
    st.header("Job Browser")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        job_type_filter = st.selectbox(
            "Filter by Job Type",
            ["All", "remote", "onsite", "full_time", "external", "unknown"]
        )
    with col2:
        location_search = st.text_input(
            "Search by Location",
            placeholder="e.g. India, London, Berlin"
        )
    with col3:
        skill_search = st.text_input("Search by Skill", placeholder="e.g. python")
    with col4:
        limit = st.slider("Number of jobs", 5, 50, 10)


    with Session(engine) as session:
        query = session.query(Job)
        if job_type_filter != "All":
            query = query.filter_by(job_type=job_type_filter)
        if location_search:
            query = query.filter(Job.location.contains(location_search))
        if skill_search:
            search_term = skill_search.lower()
            query = query.filter(
                Job.tags.contains(search_term) |
                Job.title.contains(search_term) |
                Job.description.contains(search_term)
            )
        jobs = query.limit(limit).all()

    st.write(f"[INFO] Showing {len(jobs)} jobs")
    for job in jobs:
        with st.expander(f"{job.title} at {job.company}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Location: {job.location}")
                st.write(f"Type: {job.job_type}")
            with col2:
                st.write(f"Skills: {job.tags}")
                if job.apply_url:
                    st.link_button("Apply Now", job.apply_url)

elif page == "Cover Letter":
    st.header("Cover Letter Generator")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. ML Engineer")
        company = st.text_input("Company Name", placeholder="e.g. Google")
    with col2:
        user_skills = st.text_area(
            "Your Skills",
            placeholder="python, sql, pandas, git"
        )
        experience = st.number_input("Years of Experience", min_value=0, max_value=30, value=1)

    if st.button("Generate Cover Letter"):
        if not job_title or not company or not user_skills:
            st.error("[ERROR] Please fill all fields")
        else:
            with st.spinner("Generating cover letter..."):
                response = requests.post(
                    f"{API_URL}/cover-letter",
                    json={
                        "job_title": job_title,
                        "company": company,
                        "user_skills": user_skills,
                        "experience_years": experience
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Your Cover Letter")
                    st.markdown(clean_html(data["cover_letter"]))
                    st.download_button(
                        "Download Cover Letter",
                        data["cover_letter"],
                        file_name=f"cover_letter_{company}.txt"
                    )
                else:
                    st.error(f"[ERROR] API error: {response.status_code}")

elif page == "Interview Prep":
    st.header("Interview Preparation")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title", placeholder="e.g. ML Engineer")
    with col2:
        user_skills = st.text_area(
            "Your Skills",
            placeholder="python, sql, pandas, git"
        )

    if st.button("Get Interview Questions"):
        if not job_title or not user_skills:
            st.error("[ERROR] Please fill all fields")
        else:
            with st.spinner("Generating interview questions..."):
                response = requests.post(
                    f"{API_URL}/interview-prep",
                    json={
                        "job_title": job_title,
                        "user_skills": user_skills
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Interview Questions")
                    st.markdown(clean_html(data["interview_questions"]))
                else:
                    st.error(f"[ERROR] API error: {response.status_code}")