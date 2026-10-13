# CareerPulse - Architecture

## Purpose

A user uploads a resume or types their skills. The system:
1. Extracts skills (regex rules with context checks, matched against a list of 213 skills)
2. Normalizes synonyms (`JS` = javascript, `sklearn` = scikit-learn)
3. Calculates the match % against every job **in code**
4. Sends those real scores to an LLM, which explains gaps and next steps
5. Can also write a cover letter (facts only, `[placeholders]` for the rest) and interview questions

The match % is never produced by the LLM.

## Architecture

```
RemoteOK + Arbeitnow + Adzuna   RemoteOK + Arbeitnow + Adzuna + The Muse
        |
        v
pipeline/ingestion.py  ->  dedup (company + title + city)  ->  SQLite
        |
        v
pipeline/preprocessing.py   remove non-tech jobs, clean HTML, extract skills
        |
        v
pipeline/features.py        TF-IDF, skill columns, salary scaling
        |
        v
model/online_learner.py     River BagOfWords + MultinomialNB (job category)
        |
        v
mlops/tracking.py           MLflow runs
mlops/drift.py              drift check (basic)
mlops/evaluation.py         train/test accuracy vs majority baseline

User skills / resume PDF
        |
        v
skill_extractor + skill_matching   normalize, split required / nice-to-have
        |
        v
model/llm_coach.py          match % in code -> Groq LLM explains
        |
        v
serving/api.py (FastAPI)  ->  serving/dashboard.py (Streamlit, 4 pages)

scheduler/jobs.py           APScheduler automation
```

## Files

### pipeline/
| File | Purpose |
|---|---|
| `ingestion.py` | Fetches jobs from the APIs, saves to SQLite, skips duplicates by `job_id` and by normalized company + title + city. Defines the `Job` model. |
| `dedup.py` | Normalizes company names (removes legal suffixes and "linkedin"), titles (removes "(m/f/d)") and cities, and builds the duplicate key. |
| `dedup_cleanup.py` | One-time cleanup of duplicates already in the database. Dry run by default, `--apply` deletes. |
| `preprocessing.py` | Keeps tech jobs (title keywords), cleans HTML, extracts skills, standardizes job type. |
| `skills.py` | Master list of 213 skills. |
| `skill_extractor.py` | The single skill extractor. Ambiguous words (go, r, ray, node, agents) need context. Handles `C++` and `C#`. |
| `skill_matching.py` | Synonym map, required vs nice-to-have split, and the match % calculator. |
| `location.py` | Location matching: whole-word text, country and city lookup, US state codes, remote handling. |
| `features.py` | TF-IDF matrix (500 features), skill columns, salary scaling, job-type encoding. |

### model/
| File | Purpose |
|---|---|
| `online_learner.py` | River pipeline (BagOfWords + MultinomialNB). Category labels come from title keywords. |
| `llm_coach.py` | Finds matching jobs, calls Groq (`openai/gpt-oss-20b`), writes the analysis, cover letter and interview questions. |
| `resume_parser.py` | Reads PDF text with PyMuPDF, finds skills, estimates years of experience, extracts name, email and phone. |

### mlops/
| File | Purpose |
|---|---|
| `tracking.py` | Trains and logs runs to MLflow (SQLite backend). |
| `drift.py` | Compares current data with a saved reference: schema, job-type/source shares, and row count. |
| `evaluation.py` | 5 stratified train/test splits, majority baseline, macro F1, per-class precision/recall. Writes `model_eval.json` for the sidebar. |

### serving/ and scheduler/
| File | Purpose |
|---|---|
| `serving/api.py` | FastAPI: `/`, `/health`, `/stats`, `/jobs`, `/analyze`, `/upload-resume`, `/cover-letter`, `/interview-prep`. |
| `serving/dashboard.py` | Streamlit: Resume Analyzer, Job Browser, Cover Letter, Interview Prep, sidebar stats. |
| `scheduler/jobs.py` | Full pipeline daily at 06:00; ingestion at 00:00, 06:00, 12:00 and 18:00. Runs only while the process is running. |

### Other
| Path | Purpose |
|---|---|
| `tests/` | pytest suite (67 tests). `try_*.py` files are manual check scripts. |
| `.github/workflows/tests.yml` | Runs pytest on every push. |
| `data/database/careerpulse.db` | SQLite jobs database. |
| `data/feature_store/` | TF-IDF files, scaler, model, metrics, `model_eval.json`. |
| `data/mlflow/` | MLflow tracking database. |
| `data/raw/` | Temporary storage for uploaded PDFs. |
| `data/last_updated.txt` | Time of the last ingestion. |
| `Dockerfile`, `docker-compose.yml` | Container setup. Not yet tested. |
| `db_viewer.py` | Small tool to look inside the database. |

## Tech stack

| Area | Tools |
|---|---|
| Language | Python 3.13 |
| Data | SQLite, SQLAlchemy, pandas, scikit-learn (TF-IDF) |
| Skill extraction | regex with context rules (spaCy and NLTK are installed but not used for extraction) |
| Online learning | River |
| LLM | Groq API, `openai/gpt-oss-20b` |
| PDF | PyMuPDF |
| Tracking | MLflow |
| Serving | FastAPI + uvicorn, Streamlit |
| Automation | APScheduler |
| Quality | pytest, GitHub Actions |

## Data flow

### Scheduled run (when the scheduler is running)
```
06:00  ingestion -> preprocessing -> features -> training (MLflow) -> drift check
```
If drift is flagged, training runs again.

### User request
```
Resume PDF or typed skills
  -> skills extracted and normalized
  -> every job gets a match % (required skills only)
  -> top matches sorted
  -> real scores sent to the LLM
  -> analysis shown on the dashboard
```

## Known gaps

- Drift can fire just because the job count changed.
- The category model is weak and its labels come from title keywords (see README, Model evaluation).
- The Muse adds few tech jobs (19 of 100 fetched were kept on 13 Oct 2026).
- Not deployed.