import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine

DRIFT_REPORT_PATH = "data/feature_store/drift_report.pkl"
REFERENCE_DATA_PATH = "data/feature_store/reference_data.pkl"

def get_current_data():
    print("[INFO] Loading current data from database...")
    with Session(engine) as session:
        jobs = session.query(Job).all()
        data = []
        for job in jobs:
            data.append({
                "title": job.title or "",
                "job_type": job.job_type or "",
                "tags": job.tags or "",
                "source": job.source or "",
                "salary_min": job.salary_min or 0,
                "salary_max": job.salary_max or 0,
            })
    df = pd.DataFrame(data)
    print(f"[SUCCESS] Loaded {len(df)} jobs")
    return df

def save_reference_data(df):
    print("[INFO] Saving reference data...")
    with open(REFERENCE_DATA_PATH, "wb") as f:
        pickle.dump(df, f)
    print("[SUCCESS] Reference data saved")

def load_reference_data():
    if not os.path.exists(REFERENCE_DATA_PATH):
        print("[WARNING] No reference data found")
        return None
    with open(REFERENCE_DATA_PATH, "rb") as f:
        df = pickle.load(f)
    print(f"[SUCCESS] Reference data loaded: {len(df)} jobs")
    return df

def check_schema_drift(reference_df, current_df):
    print("[INFO] Checking schema drift...")
    ref_cols = set(reference_df.columns)
    cur_cols = set(current_df.columns)
    new_cols = cur_cols - ref_cols
    missing_cols = ref_cols - cur_cols
    if new_cols:
        print(f"[WARNING] New columns detected: {new_cols}")
    if missing_cols:
        print(f"[WARNING] Missing columns: {missing_cols}")
    if not new_cols and not missing_cols:
        print("[SUCCESS] No schema drift detected")
    return len(new_cols) > 0 or len(missing_cols) > 0

def check_distribution_drift(reference_df, current_df):
    print("[INFO] Checking distribution drift...")
    drift_detected = False

    ref_job_types = reference_df["job_type"].value_counts(normalize=True)
    cur_job_types = current_df["job_type"].value_counts(normalize=True)
    all_types = set(ref_job_types.index) | set(cur_job_types.index)
    for job_type in all_types:
        ref_pct = ref_job_types.get(job_type, 0)
        cur_pct = cur_job_types.get(job_type, 0)
        diff = abs(ref_pct - cur_pct)
        if diff > 0.1:
            print(f"[WARNING] Job type drift: {job_type} changed by {diff:.2%}")
            drift_detected = True

    ref_sources = reference_df["source"].value_counts(normalize=True)
    cur_sources = current_df["source"].value_counts(normalize=True)
    all_sources = set(ref_sources.index) | set(cur_sources.index)
    for source in all_sources:
        ref_pct = ref_sources.get(source, 0)
        cur_pct = cur_sources.get(source, 0)
        diff = abs(ref_pct - cur_pct)
        if diff > 0.1:
            print(f"[WARNING] Source drift: {source} changed by {diff:.2%}")
            drift_detected = True

    if not drift_detected:
        print("[SUCCESS] No distribution drift detected")
    return drift_detected

def check_data_volume_drift(reference_df, current_df):
    print("[INFO] Checking data volume drift...")
    ref_count = len(reference_df)
    cur_count = len(current_df)
    diff_pct = abs(cur_count - ref_count) / ref_count if ref_count > 0 else 0
    print(f"[INFO] Reference jobs: {ref_count} | Current jobs: {cur_count}")
    if diff_pct > 0.2:
        print(f"[WARNING] Volume drift detected: {diff_pct:.2%} change")
        return True
    print("[SUCCESS] No volume drift detected")
    return False

def run_drift_detection():
    print(f"[INFO] Drift Detection Started: {datetime.now()}")
    current_df = get_current_data()
    reference_df = load_reference_data()
    if reference_df is None:
        print("[INFO] No reference data found, saving current as reference...")
        save_reference_data(current_df)
        print("[INFO] Run drift detection again after next ingestion")
        return False
    schema_drift = check_schema_drift(reference_df, current_df)
    distribution_drift = check_distribution_drift(reference_df, current_df)
    volume_drift = check_data_volume_drift(reference_df, current_df)
    any_drift = schema_drift or distribution_drift or volume_drift
    report = {
        "timestamp": datetime.now().isoformat(),
        "schema_drift": schema_drift,
        "distribution_drift": distribution_drift,
        "volume_drift": volume_drift,
        "any_drift": any_drift,
        "reference_count": len(reference_df),
        "current_count": len(current_df),
    }
    with open(DRIFT_REPORT_PATH, "wb") as f:
        pickle.dump(report, f)
    if any_drift:
        print(f"[WARNING] Drift detected! Model retraining recommended")
    else:
        print(f"[SUCCESS] No drift detected. Model is stable")
    return any_drift

def auto_retrain_if_drift():
    drift = run_drift_detection()
    if drift:
        print("[INFO] Drift detected, triggering retraining...")
        from mlops.tracking import train_with_tracking, setup_mlflow
        from model.online_learner import prepare_training_data
        df = prepare_training_data()
        train_with_tracking(df)
        print("[SUCCESS] Model retrained due to drift")
    else:
        print("[INFO] No retraining needed")

if __name__ == "__main__":
    run_drift_detection()