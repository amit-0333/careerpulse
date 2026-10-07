# CareerPulse - Project Architecture & File Description

## What is CareerPulse?

CareerPulse is a production-grade MLOps system that acts as an AI-powered personal career assistant. It fetches live job data daily from multiple APIs, processes and stores it in a database, trains an online learning model that continuously improves, and uses an LLM as a personal career coach that analyzes your resume, calculates real skill match percentages, identifies gaps, and provides a personalized learning roadmap.

## Core Purpose

A user uploads their resume or enters their skills. The system:
1. Extracts skills from their resume using NLP
2. Calculates REAL match percentage between their skills and every job in the database
3. Sends those REAL scores to an LLM (not hallucinated ones)
4. LLM responds with readiness assessment, jobs to apply for now, skill gaps, and a 90-day learning roadmap
5. User can also generate cover letters and get interview preparation questions

---

## Full Architecture

```
Data Sources (4 APIs)
    RemoteOK + Arbeitnow + The Muse + Adzuna
            |
            v
    Data Ingestion Layer
    pipeline/ingestion.py
            |
            v
    SQLite Database
    data/database/careerpulse.db
            |
            v
    Preprocessing Layer
    pipeline/preprocessing.py
    (removes non-tech jobs, cleans HTML, extracts skills)
            |
            v
    Feature Engineering Layer
    pipeline/features.py
    (TF-IDF, skill vectors, salary normalization)
            |
            v
    Online Learning Layer
    model/online_learner.py
    (River MultinomialNB, trains incrementally)
            |
            v
    MLOps Layer
    mlops/tracking.py + mlops/drift.py
    (MLflow experiment tracking, drift detection)
            |
            v
    LLM Intelligence Layer
    model/llm_coach.py
    (Groq API, real match calculation, career coaching)
            |
            v
    Resume Parser
    model/resume_parser.py
    (PyMuPDF, skill extraction from PDF)
            |
            v
    API Serving Layer
    serving/api.py
    (FastAPI REST API)
            |
            v
    Dashboard Layer
    serving/dashboard.py
    (Streamlit, 4 pages)
            |
            v
    Automation Layer
    scheduler/jobs.py
    (APScheduler, runs full pipeline every 24hrs)
```

---

## File Structure and Purpose

### pipeline/

| File | Purpose |
|------|---------|
| `ingestion.py` | Fetches jobs from 4 APIs (RemoteOK, Arbeitnow, The Muse, Adzuna). Saves to SQLite with duplicate detection. Creates Job SQLAlchemy model. |
| `preprocessing.py` | Filters non-tech jobs using keyword matching on title. Removes HTML from descriptions. Extracts skills using regex word boundary matching. Standardizes job types. |
| `features.py` | Builds TF-IDF matrix (500 features) from job text. Creates binary skill features for 213 skills. Normalizes salary using MinMaxScaler. One-hot encodes job types. Saves all to feature store. |
| `skills.py` | Master skills list with 200+ skills covering all tech domains for 2026 and beyond. Single source of truth imported by all other files. |

### model/

| File | Purpose |
|------|---------|
| `online_learner.py` | River-based online learning model using BagOfWords + MultinomialNB pipeline. Assigns job categories from title. Trains incrementally on each job. Saves model as pickle. Tests predictions after training. |
| `llm_coach.py` | Core intelligence file. Calculates REAL match percentage between user skills and job requirements using set intersection. Filters jobs with 0% match. Sends real scores to Groq LLM. Returns career analysis, matching jobs, skill gaps. Also generates cover letters and interview questions. |
| `resume_parser.py` | Extracts text from PDF using PyMuPDF. Finds skills using regex word boundary matching against master skills list. Detects experience years using regex patterns. Extracts name, email, phone. |

### mlops/

| File | Purpose |
|------|---------|
| `tracking.py` | Logs every training run to MLflow SQLite backend. Tracks accuracy, total jobs, categories, training date. Shows experiment history. |
| `drift.py` | Compares current database against reference baseline. Checks schema drift, distribution drift (job types and sources), and volume drift. Auto triggers retraining if drift detected. Saves drift report. |

### serving/

| File | Purpose |
|------|---------|
| `api.py` | FastAPI REST API with endpoints: GET /, /health, /stats, /jobs. POST /analyze, /upload-resume, /cover-letter, /interview-prep. Initializes database on startup. Handles CORS for Streamlit. |
| `dashboard.py` | Streamlit dashboard with 4 pages: Resume Analyzer (upload PDF or manual skills), Job Browser (filter by type, location, skill), Cover Letter Generator, Interview Prep. Shows live system stats in sidebar. |

### scheduler/

| File | Purpose |
|------|---------|
| `jobs.py` | APScheduler with two jobs: full pipeline runs daily at 6AM (ingestion + preprocessing + features + training + drift detection), data ingestion runs every 6 hours for fresh job data. |

### Root Files

| File | Purpose |
|------|---------|
| `.env` | Stores API keys securely (never pushed to GitHub) |
| `requirements.txt` | All Python dependencies with versions |
| `Dockerfile` | Docker image definition for containerization |
| `docker-compose.yml` | Multi-service Docker setup (API + Dashboard + Scheduler) |
| `.gitignore` | Excludes venv, database, feature store, API keys from GitHub |
| `.dockerignore` | Excludes unnecessary files from Docker image |
| `db_viewer.py` | Utility to view database contents, search jobs, filter by type |

### data/

| Folder | Purpose |
|--------|---------|
| `database/careerpulse.db` | SQLite database storing all jobs |
| `feature_store/` | TF-IDF matrix, vectorizer, scaler, trained model, metrics |
| `mlflow/` | MLflow experiment tracking database |
| `raw/` | Temporary storage for uploaded resume PDFs |
| `last_updated.txt` | Timestamp of last successful data ingestion |

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Language | Python 3.13 | Industry standard for ML |
| Database | SQLite | Zero setup, file-based, portable |
| ORM | SQLAlchemy | Clean database abstraction |
| NLP | spaCy, NLTK, regex | Text processing and skill extraction |
| ML Features | scikit-learn TF-IDF | Text vectorization |
| Online Learning | River | Designed for streaming/incremental data |
| LLM | Groq API (gpt-oss-20b) | Fast, free, high quality responses |
| Resume Parsing | PyMuPDF | Fast, accurate PDF text extraction |
| Experiment Tracking | MLflow | Industry standard MLOps tool |
| Drift Detection | Custom pipeline | Detects data distribution changes |
| API | FastAPI + uvicorn | Modern, fast, auto-docs |
| Dashboard | Streamlit | Perfect for data science apps |
| Scheduling | APScheduler | Reliable Python job scheduler |
| Containerization | Docker + compose | Production deployment |
| Version Control | Git + GitHub | Code management |
| Deployment | Render.com | Free cloud hosting |

---

## Data Flow

### Daily Automated Flow (when deployed):
```
6:00 AM - Scheduler triggers full pipeline
6:01 AM - Ingestion fetches new jobs from 4 APIs
6:05 AM - Preprocessing filters and cleans jobs
6:08 AM - Features built from clean data
6:10 AM - Online learning model updates itself
6:12 AM - MLflow logs new training run
6:13 AM - Drift detection checks for changes
6:14 AM - If drift detected, extra retraining triggered
6:15 AM - System ready with fresh data
```

### User Request Flow:
```
User uploads resume PDF
    -> PyMuPDF extracts text
    -> Regex finds skills in text
    -> Skills compared to every job in DB
    -> Real match % calculated per job
    -> Top matches sorted by %
    -> Real scores sent to Groq LLM
    -> LLM generates personalized analysis
    -> Results displayed on dashboard
```