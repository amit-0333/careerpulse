# CareerPulse 🎯

An AI-powered career assistant that matches your skills to real job openings, identifies skill gaps, and provides personalized career guidance using LLMs.

## What it does

- Fetches live job data daily from 4 APIs (RemoteOK, Arbeitnow, The Muse, Adzuna)
- Parses your resume (PDF) and extracts skills automatically
- Calculates real match % between your skills and job requirements
- Uses Groq LLM to provide personalized career coaching
- Generates cover letters and interview preparation questions
- Continuously retrains ML model as new jobs arrive (online learning)
- Tracks all experiments with MLflow
- Detects data drift and auto-retrains model

## Tech Stack

- Data Pipeline: Python, SQLAlchemy, SQLite
- NLP: spaCy, NLTK, TF-IDF
- Online Learning: River (MultinomialNB)
- LLM: Groq API (openai/gpt-oss-20b)
- Experiment Tracking: MLflow
- Drift Detection: Custom pipeline
- API: FastAPI
- Dashboard: Streamlit
- Containerization: Docker
- Scheduler: APScheduler

## Project Structure
careerpulse/
├── pipeline/ # Data ingestion, preprocessing, features
├── model/ # Online learning, LLM coach, resume parser
├── mlops/ # MLflow tracking, drift detection
├── serving/ # FastAPI + Streamlit dashboard
├── scheduler/ # APScheduler for automation
├── Dockerfile
└── docker-compose.yml


## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run data pipeline
python -m pipeline.ingestion
python -m pipeline.preprocessing
python -m pipeline.features
python -m model.online_learner

# Run API
python -m serving.api

# Run Dashboard
python -m streamlit run serving/dashboard.py
```

## Live Demo

Coming soon after cloud deployment.
