# CareerPulse Run Guide

All commands run from the project root with the virtual environment active.

## 0. Activate the virtual environment

Linux / macOS:
```bash
source venv/bin/activate
```

Windows (PowerShell):
```powershell
venv\Scripts\activate
```

## 1. Build the data (run in this order)

```bash
python -m pipeline.ingestion        # fetch jobs from the APIs
python -m pipeline.preprocessing    # remove non-tech jobs, clean text, extract skills
python -m pipeline.features         # build TF-IDF and skill features
python -m model.online_learner      # train the River model
python -m mlops.tracking            # log a training run to MLflow
python -m mlops.drift               # check for data drift
python -m mlops.evaluation          # honest test-set accuracy vs baseline
```

Notes:
- Ingestion can re-add non-tech jobs that preprocessing removed earlier. Run preprocessing again afterwards.
- `mlops.drift` can report "volume drift" simply because new jobs were added (see Limitations in the README).

## 2. Start the app (two terminals, venv active in both)

```bash
# Terminal 1
python -m serving.api

# Terminal 2
python -m streamlit run serving/dashboard.py
```

Use `python -m streamlit ...`, not `streamlit run ...`. Otherwise Python cannot find the `pipeline` package.

## 3. Optional

```bash
python -m scheduler.jobs            # automation: full pipeline daily at 6 AM, ingestion every 6 hours
python -m pipeline.dedup_cleanup    # dry run: list duplicate jobs (changes nothing)
python -m pipeline.dedup_cleanup --apply   # delete the duplicates
python db_viewer.py                 # look inside the database
python -m pytest -q                 # run the tests
```

The scheduler only runs while its terminal stays open.

## Fresh start (delete the database)

Linux / macOS:
```bash
rm data/database/careerpulse.db
```

Windows (PowerShell):
```powershell
del data\database\careerpulse.db
```

Then run the "Build the data" commands again.

## Back up before risky steps

`preprocessing` and `dedup_cleanup --apply` change the database permanently. Copy it first:

Linux / macOS: `cp data/database/careerpulse.db data/database/careerpulse_backup.db`

Windows: `copy data\database\careerpulse.db data\database\careerpulse_backup.db`

Backup `.db` files are ignored by git.

## What each command does

| Command | What it does |
|---|---|
| `pipeline.ingestion` | Fetches jobs from RemoteOK, Arbeitnow and Adzuna and skips duplicates (The Muse currently returns 403) |
| `pipeline.preprocessing` | Removes non-tech jobs, cleans text, extracts skills |
| `pipeline.features` | Builds TF-IDF and skill feature files |
| `model.online_learner` | Trains the River category model |
| `mlops.tracking` | Trains and logs the run to MLflow |
| `mlops.drift` | Compares current data with the reference data |
| `mlops.evaluation` | Train/test evaluation with baseline and per-class scores |
| `serving.api` | FastAPI on port 8000 |
| `serving/dashboard.py` | Streamlit on port 8501 |
| `scheduler.jobs` | Runs the pipeline on a schedule |

## URLs when running locally

| Service | URL |
|---|---|
| Dashboard | http://localhost:8501 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Stats | http://localhost:8000/stats |

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'pipeline'` | Use `python -m streamlit run ...` from the project root |
| `No module named 'river'` (or other) | Activate the venv, then `pip install -r requirements.txt` |
| AI features fail | Check `GROQ_API_KEY` in `.env` |
| Sidebar shows "not evaluated" | Run `python -m mlops.evaluation` |