import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = BlockingScheduler()

def run_ingestion():
    print(f"[SCHEDULER] Running ingestion: {datetime.now()}")
    try:
        from pipeline.ingestion import fetch_remoteok, fetch_arbeitnow, fetch_themuse, fetch_adzuna, save_jobs
        all_jobs = []
        all_jobs.extend(fetch_remoteok())
        all_jobs.extend(fetch_arbeitnow())
        all_jobs.extend(fetch_themuse())
        all_jobs.extend(fetch_adzuna())
        save_jobs(all_jobs)
        print(f"[SCHEDULER] Ingestion complete: {len(all_jobs)} jobs fetched")
    except Exception as e:
        print(f"[ERROR] Ingestion failed: {e}")

def run_preprocessing():
    print(f"[SCHEDULER] Running preprocessing: {datetime.now()}")
    try:
        from pipeline.preprocessing import preprocess_jobs
        preprocess_jobs()
        print(f"[SCHEDULER] Preprocessing complete")
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}")

def run_features():
    print(f"[SCHEDULER] Running feature engineering: {datetime.now()}")
    try:
        from pipeline.features import build_features
        build_features()
        print(f"[SCHEDULER] Feature engineering complete")
    except Exception as e:
        print(f"[ERROR] Feature engineering failed: {e}")

def run_training():
    print(f"[SCHEDULER] Running model training: {datetime.now()}")
    try:
        from mlops.tracking import train_with_tracking, setup_mlflow
        from model.online_learner import prepare_training_data
        df = prepare_training_data()
        train_with_tracking(df)
        print(f"[SCHEDULER] Training complete")
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")

def run_drift_detection():
    print(f"[SCHEDULER] Running drift detection: {datetime.now()}")
    try:
        from mlops.drift import auto_retrain_if_drift
        auto_retrain_if_drift()
        print(f"[SCHEDULER] Drift detection complete")
    except Exception as e:
        print(f"[ERROR] Drift detection failed: {e}")

def run_full_pipeline():
    print(f"[SCHEDULER] Full pipeline started: {datetime.now()}")
    run_ingestion()
    run_preprocessing()
    run_features()
    run_training()
    run_drift_detection()
    print(f"[SCHEDULER] Full pipeline completed: {datetime.now()}")

# runs every day at 6AM
scheduler.add_job(
    run_full_pipeline,
    CronTrigger(hour=6, minute=0),
    id="daily_pipeline",
    name="Daily Full Pipeline",
    replace_existing=True
)

# runs every 6 hours for fresh job data
scheduler.add_job(
    run_ingestion,
    CronTrigger(hour="0,6,12,18", minute=0),
    id="ingestion_6hr",
    name="6 Hour Ingestion",
    replace_existing=True
)

if __name__ == "__main__":
    print(f"[INFO] CareerPulse Scheduler Started: {datetime.now()}")
    print(f"[INFO] Full pipeline runs daily at 6AM")
    print(f"[INFO] Ingestion runs every 6 hours")
    print(f"[INFO] Press Ctrl+C to stop")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print(f"[INFO] Scheduler stopped")
        scheduler.shutdown()