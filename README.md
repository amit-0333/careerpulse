# CareerPulse - AI Powered Career Assistant

<!-- Add your banner image here -->
<!-- ![CareerPulse Banner](demo/banner.png) -->

## What is CareerPulse?

CareerPulse is a production-grade MLOps system that acts as your personal AI career coach. It fetches live job data daily from multiple APIs, calculates real skill match percentages between your profile and job requirements, and uses an LLM to provide personalized career guidance.

<!-- Add dashboard screenshot here -->
<!-- ![Dashboard](demo/dashboard.png) -->

---

## The Problem it Solves

Most job search tools show you jobs without telling you:
- How well you actually match the requirements
- Which specific skills you are missing
- What to learn to become a better candidate
- Which jobs you can realistically apply for right now

CareerPulse solves all of this with real data, not guesses.

---

## Key Features

- **Live Job Data** - Fetches fresh jobs daily from 4 APIs covering remote, hybrid, onsite, full-time, contract roles
- **Real Match Scoring** - Calculates actual skill match percentage using set intersection algorithm, not AI estimates
- **AI Career Coach** - LLM receives real scores and provides personalized readiness assessment, apply-now list, and skill gap analysis
- **Resume Parser** - Upload your PDF resume and skills are extracted automatically
- **90-Day Roadmap** - Personalized week-by-week learning plan based on your actual gaps
- **Cover Letter Generator** - AI writes a tailored cover letter for any job
- **Interview Prep** - Get likely interview questions for any role
- **Online Learning** - ML model continuously retrains as new jobs arrive
- **Drift Detection** - Automatically detects when job market changes and triggers retraining
- **Experiment Tracking** - Every model training run logged with MLflow

---

## How it Works

```
You upload resume
        |
        v
Skills extracted from PDF using NLP
        |
        v
Real match % calculated against every job in database
(set intersection of your skills vs job requirements)
        |
        v
LLM receives REAL scores (not hallucinated)
        |
        v
Personalized analysis:
  - Readiness % based on real data
  - Jobs to apply for NOW with exact match %
  - Jobs not ready for yet with exact missing skills
  - Skill gaps detected by algorithm
  - 90 day learning roadmap
  - Cover letter generation
  - Interview questions
```

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.13 |
| Database | SQLite + SQLAlchemy |
| NLP | spaCy, NLTK, TF-IDF |
| Online Learning | River (MultinomialNB) |
| LLM | Groq API (free) |
| Experiment Tracking | MLflow |
| Drift Detection | Custom pipeline |
| API | FastAPI |
| Dashboard | Streamlit |
| Scheduler | APScheduler |
| Containerization | Docker |
| Deployment | Render.com |

---

## Project Structure

```
careerpulse/
├── pipeline/
│   ├── ingestion.py       # Fetches jobs from 4 APIs
│   ├── preprocessing.py   # Cleans and filters tech jobs
│   ├── features.py        # TF-IDF and skill feature engineering
│   └── skills.py          # Master skills list (200+ skills)
├── model/
│   ├── online_learner.py  # River incremental learning model
│   ├── llm_coach.py       # Groq LLM career coaching
│   └── resume_parser.py   # PDF resume skill extraction
├── mlops/
│   ├── tracking.py        # MLflow experiment tracking
│   └── drift.py           # Data drift detection
├── serving/
│   ├── api.py             # FastAPI REST API
│   └── dashboard.py       # Streamlit dashboard
├── scheduler/
│   └── jobs.py            # APScheduler automation
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Dashboard Pages

<!-- Add screenshots for each page -->

### Resume Analyzer
Upload your PDF resume or enter skills manually. Get real match percentages against live job database plus full AI career analysis.
<!-- ![Resume Analyzer](demo/resume_analyzer.png) -->

### Job Browser
Browse all jobs with filters for job type, location search, and skill search. Direct apply links to company career portals.
<!-- ![Job Browser](demo/job_browser.png) -->

### Cover Letter Generator
Select any job, enter your skills, get a tailored professional cover letter in seconds. Download as text file.
<!-- ![Cover Letter](demo/cover_letter.png) -->

### Interview Prep
Get 8 likely interview questions (technical, behavioral, system design) with tips on how to answer each one.
<!-- ![Interview Prep](demo/interview_prep.png) -->

---

## System Stats (Live)

The sidebar shows real-time system metrics:
- Total jobs in database
- Remote jobs available
- Most in-demand skill
- Model accuracy (improves daily)
- Last data update timestamp

---

## MLOps Pipeline

```
Daily at 6AM (automated):
  1. Fetch new jobs from 4 APIs
  2. Filter and clean data
  3. Build features
  4. Retrain online learning model
  5. Log run to MLflow
  6. Check for data drift
  7. Auto-retrain if drift detected
```

---

## How to Run Locally

```bash
# Clone repo
git clone https://github.com/amit-0333/careerpulse.git
cd careerpulse

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add API keys to .env file
# GROQ_API_KEY=your_key
# MUSE_API_KEY=your_key

# Run data pipeline
python -m pipeline.ingestion
python -m pipeline.preprocessing
python -m pipeline.features
python -m model.online_learner

# Start API (Terminal 1)
python -m serving.api

# Start Dashboard (Terminal 2)
python -m streamlit run serving/dashboard.py
```

Open http://localhost:8501 in browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | / | API info |
| GET | /health | Health check |
| GET | /stats | Database stats |
| GET | /jobs | Browse jobs |
| POST | /analyze | Analyze skills against jobs |
| POST | /upload-resume | Upload PDF and analyze |
| POST | /cover-letter | Generate cover letter |
| POST | /interview-prep | Get interview questions |

API Docs: http://localhost:8000/docs

---

## Demo

<!-- Add your demo video/GIF here -->
<!-- ![Demo GIF](demo/careerpulse_demo.gif) -->
<!-- [Watch Full Demo Video](demo/careerpulse_demo.mp4) -->

---

## Live Deployment

- API: Coming soon
- Dashboard: Coming soon 

---

## Author

**Amit Kumar**
- GitHub: [@amit-0333](https://github.com/amit-0333)

---

## License

MIT License