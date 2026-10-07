# CareerPulse Run Guide

## How to Start Everything

### Step 1 - Activate Virtual Environment
```bash
cd "C:\DSMP PROJECTS\careerpulse"
venv\Scripts\activate
```

### Step 2 - Add New Jobs to Database
```bash
python -m pipeline.ingestion
```

### Step 3 - Clean and Filter Jobs
```bash
python -m pipeline.preprocessing
```

### Step 4 - Build Features
```bash
python -m pipeline.features
```

### Step 5 - Retrain Model
```bash
python -m model.online_learner
```

### Step 6 - Track with MLflow
```bash
python -m mlops.tracking
```

### Step 7 - Check for Drift
```bash
python -m mlops.drift
```

### Step 8 - Run API Server
```bash
python -m serving.api
```

### Step 9 - Run Dashboard (new terminal)
```bash
python -m streamlit run serving/dashboard.py
```

### Step 10 - Run Scheduler (new terminal)
```bash
python -m scheduler.jobs
```

---

## Quick Commands

### Full Pipeline Run (steps 2-7 in one go)
```bash
python -m pipeline.ingestion
python -m pipeline.preprocessing
python -m pipeline.features
python -m model.online_learner
python -m mlops.tracking
python -m mlops.drift
```

### Start App Only (after pipeline already run)
```bash
# Terminal 1
python -m serving.api

# Terminal 2
python -m streamlit run serving/dashboard.py
```

### View Database
```bash
python db_viewer.py
```

### Fresh Start (delete old database)
```bash
del data\database\careerpulse.db
python -m pipeline.ingestion
python -m pipeline.preprocessing
python -m pipeline.features
python -m model.online_learner
```

---

## What Each Step Does

| Step | Command | What it does |
|------|---------|--------------|
| Ingestion | pipeline.ingestion | Fetches live jobs from 4 APIs |
| Preprocessing | pipeline.preprocessing | Removes non-tech jobs, cleans text |
| Features | pipeline.features | Builds TF-IDF and skill features |
| Training | model.online_learner | Trains River online learning model |
| Tracking | mlops.tracking | Logs run to MLflow |
| Drift | mlops.drift | Checks if data changed significantly |
| API | serving.api | Starts FastAPI on port 8000 |
| Dashboard | serving/dashboard.py | Starts Streamlit on port 8501 |
| Scheduler | scheduler.jobs | Auto runs pipeline every 24hrs |

---

## URLs When Running Locally

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| API Health | http://localhost:8000/health |
| API Stats | http://localhost:8000/stats |