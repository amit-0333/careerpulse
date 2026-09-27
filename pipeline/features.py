import re
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import pickle
import os
from pipeline.ingestion import Job, engine
from pipeline.skills import SKILLS_LIST


def load_jobs():
    print("[INFO] Loading jobs from database...")
    with Session(engine) as session:
        jobs = session.query(Job).all()
        data = []
        for job in jobs:
            data.append({
                "job_id": job.job_id,
                "title": job.title or "",
                "company": job.company or "",
                "description": job.description or "",
                "location": job.location or "",
                "job_type": job.job_type or "",
                "salary_min": job.salary_min or 0,
                "salary_max": job.salary_max or 0,
                "tags": job.tags or "",
                "source": job.source or "",
            })
    df = pd.DataFrame(data)
    print(f"[SUCCESS] Loaded {len(df)} jobs")
    return df

def build_text_features(df):
    print("[INFO] Building TF-IDF features...")
    df["combined_text"] = (
        df["title"] + " " +
        df["description"] + " " +
        df["tags"]
    )
    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words="english",
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(df["combined_text"])
    print(f"[SUCCESS] TF-IDF matrix shape: {tfidf_matrix.shape}")
    return tfidf_matrix, vectorizer

def build_skill_features(df):
    print("[INFO] Building skill features...")
    skill_cols = {}
    for skill in SKILLS_LIST:
        clean_skill = skill.replace(" ", "_").replace("/", "_")
        pattern = r'\b' + re.escape(skill) + r'\b'
        skill_cols[f"skill_{clean_skill}"] = df["tags"].str.lower().apply(
            lambda x: 1 if re.search(pattern, str(x)) else 0
        )
    skill_df = pd.DataFrame(skill_cols, index=df.index)
    df = pd.concat([df, skill_df], axis=1)
    print(f"[SUCCESS] Skill features built: {len(skill_cols)} skills")
    return df

def build_salary_features(df):
    print("[INFO] Normalizing salary features...")
    scaler = MinMaxScaler()
    df["salary_min"] = df["salary_min"].fillna(0)
    df["salary_max"] = df["salary_max"].fillna(0)
    df[["salary_min_scaled", "salary_max_scaled"]] = scaler.fit_transform(
        df[["salary_min", "salary_max"]]
    )
    print("[SUCCESS] Salary features normalized")
    return df, scaler

def build_jobtype_features(df):
    print("[INFO] Building job type features...")
    df = pd.get_dummies(df, columns=["job_type"], prefix="type")
    print("[SUCCESS] Job type features built")
    return df

def save_features(df, tfidf_matrix, vectorizer, scaler):
    print("[INFO] Saving features...")
    os.makedirs("data/feature_store", exist_ok=True)
    df.to_csv("data/feature_store/jobs_features.csv", index=False)
    with open("data/feature_store/tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("data/feature_store/salary_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    import scipy.sparse as sp
    sp.save_npz("data/feature_store/tfidf_matrix.npz", tfidf_matrix)
    print("[SUCCESS] Features saved to data/feature_store/")

def build_features():
    print(f"[INFO] Starting feature engineering...")
    df = load_jobs()
    tfidf_matrix, vectorizer = build_text_features(df)
    df = build_skill_features(df)
    df, scaler = build_salary_features(df)
    df = build_jobtype_features(df)
    save_features(df, tfidf_matrix, vectorizer, scaler)
    print(f"[SUCCESS] Feature engineering complete!")
    print(f"[INFO] Total features: {len(df.columns)}")
    print(f"[INFO] Total jobs: {len(df)}")
    return df, tfidf_matrix, vectorizer, scaler

if __name__ == "__main__":
    build_features()