# CareerPulse 🎯

An AI-powered career assistant that matches your skills to real job openings, identifies skill gaps, and provides personalized career guidance using machine learning and LLMs.

## What It Does

- Fetches live job data from RemoteOK, Arbeitnow, The Muse, and Adzuna
- Parses resumes in PDF format and extracts relevant skills
- Calculates job match percentage based on skills and job requirements
- Identifies missing skills and skill gaps
- Uses Groq LLM for personalized career coaching
- Generates personalized cover letters
- Generates interview preparation questions
- Continuously updates the ML model as new job data arrives
- Tracks experiments and model performance using MLflow
- Detects data drift and supports model retraining
- Provides REST APIs using FastAPI
- Provides an interactive dashboard using Streamlit
- Automates data ingestion and model updates using APScheduler

## Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Data Pipeline | Python, SQLAlchemy, SQLite |
| Data Processing | Pandas, NumPy |
| NLP | spaCy, NLTK, TF-IDF |
| Machine Learning | River, MultinomialNB |
| LLM | Groq API |
| LLM Model | `openai/gpt-oss-20b` |
| Experiment Tracking | MLflow |
| API | FastAPI |
| Dashboard | Streamlit |
| Database | SQLite |
| Scheduler | APScheduler |
| Containerization | Docker |
| Job APIs | RemoteOK, Arbeitnow, The Muse, Adzuna |

## Project Structure

```text
careerpulse/
│
├── pipeline/
│   ├── __init__.py
│   ├── ingestion.py
│   ├── preprocessing.py
│   └── features.py
│
├── model/
│   ├── __init__.py
│   ├── online_learner.py
│   ├── resume_parser.py
│   └── llm_coach.py
│
├── mlops/
│   ├── __init__.py
│   ├── mlflow_tracking.py
│   └── drift_detection.py
│
├── serving/
│   ├── __init__.py
│   ├── api.py
│   └── dashboard.py
│
├── scheduler/
│   ├── __init__.py
│   └── scheduler.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── careerpulse.db
│
├── experiments/
│   └── mlruns/
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_model.py
│   └── test_api.py
│
├── .env
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## System Architecture

```text
                    ┌─────────────────────┐
                    │      Job APIs       │
                    │                     │
                    │     RemoteOK        │
                    │     Arbeitnow       │
                    │     The Muse        │
                    │     Adzuna          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Data Pipeline    │
                    │                     │
                    │    Ingestion        │
                    │    Preprocessing    │
                    │    Feature Eng.     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   SQLite Database   │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
      ┌─────────────────┐           ┌─────────────────┐
      │  Online ML      │           │  Resume Parser  │
      │     Model       │           │                 │
      │                 │           │  PDF → Skills   │
      │  River          │           │  NLP            │
      │  MultinomialNB  │           │                 │
      └────────┬────────┘           └────────┬────────┘
               │                             │
               └──────────────┬──────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Career Matching   │
                    │                     │
                    │   Match %           │
                    │   Skill Gaps        │
                    │   Recommendations   │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌─────────────────┐         ┌─────────────────┐
       │    FastAPI      │         │    Streamlit    │
       │      API        │         │    Dashboard    │
       └────────┬────────┘         └────────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │        User         │
                    │                     │
                    │  Job Matching       │
                    │  Resume Analysis    │
                    │  Career Coaching    │
                    │  Cover Letters      │
                    │  Interview Prep     │
                    └─────────────────────┘
```

## MLOps Pipeline

```text
New Jobs
   │
   ▼
Data Ingestion
   │
   ▼
Preprocessing
   │
   ▼
Feature Engineering
   │
   ▼
Online Learning
   │
   ▼
Model Evaluation
   │
   ├──────────────► MLflow Tracking
   │
   ▼
Drift Detection
   │
   ├── No Drift ─────────► Continue Monitoring
   │
   └── Drift Detected ──► Retrain Model
```

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/amit-0333/careerpulse.git
cd careerpulse
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

### 5. Run the Data Pipeline

Run job ingestion:

```bash
python -m pipeline.ingestion
```

Run preprocessing:

```bash
python -m pipeline.preprocessing
```

Run feature engineering:

```bash
python -m pipeline.features
```

### 6. Run the Machine Learning Model

```bash
python -m model.online_learner
```

### 7. Start the FastAPI Server

```bash
python -m serving.api
```

API:

```text
http://localhost:8000
```

### 8. Start the Streamlit Dashboard

```bash
python -m streamlit run serving/dashboard.py
```

Dashboard:

```text
http://localhost:8501
```

## Docker

Build and start the application:

```bash
docker-compose up --build
```

Stop the containers:

```bash
docker-compose down
```

## Core Features

### Job Matching

CareerPulse compares user skills with job requirements and calculates a job match percentage.

### Resume Analysis

Users can upload a PDF resume. The system extracts relevant information and skills using NLP techniques.

### Skill Gap Detection

The system identifies skills required by a job that are missing from the user's profile.

### AI Career Coach

The Groq LLM provides personalized career guidance based on the user's resume, skills, target role, and selected job.

### Cover Letter Generation

CareerPulse generates job-specific cover letters based on the candidate's profile and job requirements.

### Interview Preparation

The system generates technical and behavioral interview questions based on the selected role and job requirements.

### Online Learning

The ML model continuously learns from newly ingested job data using River's online learning framework.

### MLOps

MLflow tracks experiments and model performance, while the drift detection pipeline monitors changes in incoming job data.

## Data Sources

CareerPulse currently integrates with:

- RemoteOK
- Arbeitnow
- The Muse
- Adzuna

The ingestion pipeline normalizes job information from these sources into a common structure before storing it in the database.

## Future Improvements

- Personalized job recommendations
- Additional job-board integrations
- Semantic job matching using embeddings
- User authentication and profiles
- Job application tracking
- Email notifications for relevant jobs
- Automated resume improvement suggestions
- Advanced model monitoring
- Cloud deployment
- Production database integration

## Live Demo

Coming soon after cloud deployment.
