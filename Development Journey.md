# CareerPulse - Development Journey

## Phase-wise Development Log

---

## Phase 1 - Data Ingestion Pipeline

### What I Built
Connected 4 free job APIs: RemoteOK, Arbeitnow, The Muse, and Adzuna. Built a pipeline that fetches live job data and stores it in a SQLite database with duplicate detection.

### Problem Faced
Adzuna API was returning empty responses when API keys were missing, causing a JSON decode error and crashing the entire pipeline.

### How I Fixed It
Added try/except error handling around every API call with status code checking. If any API fails, it logs a warning and continues with the other APIs instead of crashing.

### Result
1141 jobs fetched successfully from 3 APIs even when one fails.

---

## Phase 2 - Data Cleaning and NLP

### What I Built
A preprocessing pipeline that filters non-tech jobs, removes HTML from descriptions, extracts skills using regex with word boundary matching, and standardizes job types.

### Problem Faced
The initial filter was too loose — jobs like "Office Maid", "Police Officer", and "Store Manager" were passing through because their descriptions mentioned technical words.

### How I Fixed It
Changed from description-based filtering to title-only filtering with a strict list of tech job keywords. This reduced false positives significantly.

### Second Problem
The skill extractor was matching "r" inside words like "water" and "developer", causing false skill detections.

### How I Fixed It
Replaced simple string contains with regex word boundary matching `\b` so "r" only matches as a standalone word.

### Result
399 clean tech jobs kept from 1141 total. Zero false skill detections.

---

## Phase 3 - Feature Engineering

### What I Built
TF-IDF vectorization of job text (500 features), binary skill features for 213 skills, salary normalization using MinMaxScaler, and job type one-hot encoding.

### Problem Faced
Performance warning: DataFrame was highly fragmented because skill features were being added one column at a time using insert.

### How I Fixed It
Changed to batch column creation using pd.concat(axis=1) instead of inserting one column at a time.

### Result
230 total features built for 399 jobs. Feature store saved successfully.

---

## Phase 4 - Online Learning Model

### What I Built
River-based online learning model using BagOfWords + MultinomialNB pipeline. Model trains on each job one by one and updates itself incrementally.

### Problem Faced
Tried switching to Hoeffding Tree for better accuracy but accuracy dropped from 59% to 35% because Hoeffding Tree needs much more data to work well.

### How I Fixed It
Reverted to MultinomialNB which works well with small datasets. Accuracy recovered to 54-59%.

### Second Problem
Too many jobs categorized as "other_tech" (40%+ of dataset) causing class imbalance and lower accuracy.

### How I Fixed It
This is a data volume problem not a code problem. More daily data ingestion will naturally reduce the other_tech percentage and improve accuracy over time through online learning.

### Result
Model trained at 47-59% accuracy depending on dataset size. Improves automatically as more jobs are ingested daily.

---

## Phase 5 - MLflow Experiment Tracking

### What I Built
MLflow experiment tracking using SQLite backend. Every training run logs: accuracy, total jobs, category distribution, training date, model type.

### Problem Faced
MLflow UI was broken on Windows with Python 3.13 due to uvicorn socket error [WinError 10022].

### How I Fixed It
Skipped local MLflow UI. The tracking database still works perfectly and stores all run history. UI works correctly when deployed to cloud.

### Second Problem
MLflow file store was deprecated. Got error about filesystem tracking backend being in maintenance mode.

### How I Fixed It
Switched from file store to SQLite backend: `sqlite:///data/mlflow/mlflow.db`

### Result
5+ experiment runs tracked with full history of accuracy, jobs trained, and timestamps.

---

## Phase 6 - Drift Detection

### What I Built
Custom drift detection that checks schema drift, distribution drift (job type and source percentages), and volume drift. Auto triggers retraining when drift is detected.

### Problem Faced
First run showed 74% volume drift because reference data had 168 jobs but current had 293.

### How I Fixed It
This was correct behavior not a bug. Drift detection was working exactly as designed - it detected that 125 new jobs were added and triggered retraining recommendation.

### Result
Drift detection correctly identifies when job market distribution changes and model needs updating.

---

## Phase 7 - LLM Integration

### What I Built
Groq API integration using free tier (openai/gpt-oss-20b model). Career coach that analyzes user profile against job database.

### Critical Problem Faced
LLM was hallucinating match percentages. It said "Senior ML Engineer at Voleon: 75% match" but this number was invented by the LLM, not calculated from actual data.

### How I Fixed It
Changed the flow completely:
1. Calculate REAL match % using set intersection of user skills and job required skills
2. Send those REAL scores to LLM with explicit instruction: "Do NOT change or estimate these percentages"
3. LLM now explains the real scores instead of inventing new ones

### Second Problem
Variable name conflict in get_matching_jobs function. The variable `matched` was used for both the jobs results list and the skill intersection result, causing the function to return None.

### How I Fixed It
Renamed the jobs results list from `matched` to `results` to avoid the conflict.

### Result
Real match percentages now show correctly: 100% for exact matches, 67% for one missing skill, 50% for two missing skills etc.

---

## Phase 8 - Resume Parser

### What I Built
PDF resume parser using PyMuPDF that extracts text, finds skills using regex matching, detects experience years, and extracts name, email, phone.

### Problem Faced
`import fitz` showed deprecation warning saying to use `import pymupdf` instead.

### How I Fixed It
Changed to `import pymupdf as fitz` to use the new API while keeping existing code working.

### Result
Resume parser correctly extracts skills from PDF and feeds them into the career analysis pipeline.

---

## Phase 9 - FastAPI

### What I Built
REST API with endpoints for career analysis, resume upload, cover letter generation, interview prep, job browsing, and system stats.

### Problem Faced
The 0% match issue surfaced here. All jobs were returning 0% match because of the variable name conflict bug (see Phase 7).

### How I Fixed It
Fixed the variable name conflict in get_matching_jobs (renamed matched to results).

### Result
All API endpoints working correctly. Swagger docs auto-generated at /docs.

---

## Phase 10 - Streamlit Dashboard

### What I Built
4-page dashboard: Resume Analyzer, Job Browser, Cover Letter Generator, Interview Prep. Live system stats in sidebar showing total jobs, remote jobs, top skill, model accuracy, last updated date.

### Problem Faced
HTML tags like `<br>` were showing as raw text in the LLM analysis output.

### How I Fixed It
Created a clean_html() function that replaces `<br>`, `<br/>`, and `<br />` with newline characters before rendering with st.markdown().

### Second Problem
Job Browser was showing 0 results when searching "data science" because skills stored in tags are individual words not phrases.

### How I Fixed It
Changed search to look in title, description, AND tags instead of only tags.

### Third Problem
Job type dropdown had options like hybrid, part_time, contract, internship that had 0 jobs in database.

### How I Fixed It
Queried actual job types from database and updated dropdown to match real values: remote, onsite, full_time, external, unknown.

### Fourth Problem
Last Updated date in sidebar was stale showing old date even after new ingestion.

### How I Fixed It
Added update_last_updated() function in ingestion.py that writes current timestamp to data/last_updated.txt after every successful ingestion. Dashboard reads from this file.

### Result
Full dashboard working with all 4 pages functional and accurate system stats.

---

## Phase 11 - Scheduler

### What I Built
APScheduler with two scheduled jobs: full pipeline at 6AM daily and data ingestion every 6 hours.

### Problem Faced
No issues. Scheduler worked correctly on first attempt.

### Result
Scheduler starts and waits for scheduled times. Runs automatically when deployed to cloud.

---

## Phase 12 - Docker

### What I Built
Dockerfile, docker-compose.yml for 3 services (API, Dashboard, Scheduler), and .dockerignore.

### Decision Made
Decided not to test Docker locally because:
1. Still in development phase with frequent code changes
2. Render.com reads Dockerfile from GitHub automatically
3. No need to build locally if deploying to cloud

### Result
Docker files created and ready for cloud deployment.

---

## Phase 13 - GitHub

### What I Built
Git repository with proper .gitignore excluding venv, database, feature store, API keys, and logs.

### Problem Faced
Push rejected because README was created on GitHub but not locally, causing merge conflict.

### How I Fixed It
Ran `git pull origin main --allow-unrelated-histories` to merge the remote README, then pushed successfully.

### Result
All code pushed to https://github.com/amit-0333/careerpulse

---

## Phase 14 - Cloud Deployment

### What I Built
FastAPI deployed on Render.com free tier.

### Problem Faced 1
Build failed with error: `No matching distribution found for pywin32==312`

### How I Fixed It
pywin32 is a Windows-only library that got included in requirements.txt when pip freeze was run on Windows. Removed it from requirements.txt since Render runs on Linux.

### Problem Faced 2
After build succeeded, got database error: `unable to open database file`

### How I Fixed It
Added os.makedirs() calls at the top of api.py to create all required directories on startup, and added Base.metadata.create_all(engine) to initialize the database schema.

### Problem Faced 3
Render free tier has cold start - sleeps after 15 minutes of inactivity, takes 30-60 seconds to wake up.

### Decision Made
For portfolio demo purposes, running locally is more reliable. Render URL kept for resume/LinkedIn but local demo used for interviews.

### Result
API deployed on Render. Dashboard ready for Streamlit Cloud deployment.

---

## Key Lessons Learned

1. Always use word boundary regex `\b` for skill matching to avoid false matches
2. Never let LLM generate data that should come from algorithms (match percentages)
3. Variable naming conflicts are silent bugs - use descriptive names
4. Online learning accuracy depends heavily on dataset size and class balance
5. pip freeze on Windows includes Windows-only packages that break Linux deployments
6. Free tier cloud services have cold start delays - warn users or use local demo
7. Database files should never be in .gitignore and should be initialized on startup for cloud
8. MLflow file store is deprecated - always use database backend