# CareerPulse - Development Journey

A log of what I built, what broke, and what I learned. Phases 1-14 are the original build. Phases 15-23 are an audit I did in October 2026, where I tested my own claims and fixed what did not hold up. Where a later phase proved an earlier statement wrong, the earlier phase carries a **Correction** note instead of being quietly rewritten.

---

# Part 1 - Original build

## Phase 1 - Data Ingestion Pipeline

**Built:** Connected 4 free job APIs (RemoteOK, Arbeitnow, The Muse, Adzuna) and stored jobs in SQLite with duplicate detection.

**Problem:** Adzuna returned empty responses when API keys were missing, causing a JSON decode error that crashed the pipeline.

**Fix:** try/except and status-code checks around every API call. A failing API logs a warning and the others continue.

**Result:** 1,141 jobs fetched from 3 APIs even when one failed.

**Correction (Phase 18):** duplicate detection only compared `job_id`, so the same job from two sources was never caught.

---

## Phase 2 - Data Cleaning and NLP

**Built:** Preprocessing that filters non-tech jobs, strips HTML, extracts skills with regex word boundaries, and standardizes job types.

**Problem 1:** The filter was too loose. "Office Maid" and "Police Officer" passed because descriptions mentioned technical words.
**Fix:** Filter on the title only, using a strict list of tech keywords.

**Problem 2:** The extractor matched "r" inside words like "water".
**Fix:** `\b` word boundaries so "r" only matches as a standalone word.

**Result:** 399 tech jobs kept from 1,141.

**Correction (Phase 16):** "Zero false skill detections" was wrong. `\b` still matched the English word "go" and "R" in "R&D", and it could never match `C++` or `C#`.

---

## Phase 3 - Feature Engineering

**Built:** TF-IDF (500 features), binary skill columns for 213 skills, salary scaling with MinMaxScaler, job-type one-hot encoding.

**Problem:** Pandas "DataFrame is highly fragmented" warning from adding columns one at a time.
**Fix:** Build all columns at once with `pd.concat(axis=1)`.

**Result:** 230 features for 399 jobs.

---

## Phase 4 - Online Learning Model

**Built:** River `BagOfWords + MultinomialNB`, trained one job at a time.

**Problem 1:** Hoeffding Tree dropped accuracy from 59% to 35% on this small dataset.
**Fix:** Went back to MultinomialNB.

**Problem 2:** "other_tech" was over 40% of the data.
**What I said then:** "More data will fix it and accuracy will improve automatically."

**Correction (Phase 20):** I never measured that. The later evaluation showed the labels come from title keywords and the model gains little from more data.

---

## Phase 5 - MLflow Experiment Tracking

**Built:** MLflow with a SQLite backend. Each run logs accuracy, job count, category distribution and date.

**Problem 1:** MLflow UI crashed on Windows + Python 3.13 (`WinError 10022`).
**Fix:** Skipped the local UI. The tracking database still stores every run.

**Problem 2:** The file-store backend is deprecated.
**Fix:** Switched to `sqlite:///data/mlflow/mlflow.db`.

**Result:** 8 runs recorded at my last check in October 2026.

---

## Phase 6 - Drift Detection

**Built:** Checks for schema drift, distribution drift (job type and source shares) and volume drift. Triggers retraining on drift.

**Problem:** First run reported 74% volume drift (168 reference jobs vs 293 current).
**What I said then:** "Correct behavior, not a bug."

**Correction (Phase 23):** The saved report on 1,559 jobs showed `volume_drift: True` while `distribution_drift: False`. Volume drift fires just because jobs were added, and the reference data is never refreshed, so it fires on every run. This is a known weakness.

---

## Phase 7 - LLM Integration

**Built:** Groq (`openai/gpt-oss-20b`) career coach.

**Problem 1 (critical):** The LLM invented match percentages ("75% match" was not calculated).
**Fix:** The code calculates the match % and the LLM only explains the real numbers.

**Problem 2:** A variable named `matched` was used for two things, so `get_matching_jobs` returned `None`.
**Fix:** Renamed the list to `results`.

**Result:** Real percentages (100%, 67%, 50% ...).

---

## Phase 8 - Resume Parser

**Built:** PyMuPDF parser for text, skills, experience years, name, email, phone.

**Problem:** `import fitz` gave a deprecation warning.
**Fix:** `import pymupdf as fitz`.

**Note (Phase 23):** when no experience is found the parser returns 1 year, which is a guess.

---

## Phase 9 - FastAPI

**Built:** Endpoints for analysis, resume upload, cover letter, interview prep, jobs and stats.

**Problem:** Every job showed 0% match. Cause: the Phase 7 variable bug.
**Result:** All endpoints work; Swagger docs at `/docs`.

---

## Phase 10 - Streamlit Dashboard

**Built:** 4 pages (Resume Analyzer, Job Browser, Cover Letter, Interview Prep) and a stats sidebar.

**Problems and fixes:**
- Raw `<br>` tags in LLM output -> `clean_html()` before `st.markdown()`.
- Job Browser found nothing for "data science" -> search title, description and tags.
- Job-type dropdown listed types with 0 jobs -> use the types that exist in the database.
- Stale "Last Updated" -> ingestion writes `data/last_updated.txt`.

---

## Phase 11 - Scheduler

**Built:** APScheduler: full pipeline daily at 06:00, ingestion every 6 hours.

**Note:** It only runs while its process is running. I have not run it continuously.

---

## Phase 12 - Docker

**Built:** `Dockerfile`, `docker-compose.yml` (API, dashboard, scheduler), `.dockerignore`.

**Decision:** I did not test Docker locally. **Status: still untested.**

---

## Phase 13 - GitHub

**Built:** Repository with a `.gitignore`.

**Problem:** Push rejected because a README existed only on GitHub.
**Fix:** `git pull origin main --allow-unrelated-histories`, then push.

---

## Phase 14 - Cloud Deployment (historical)

**Built:** FastAPI on Render free tier.

**Problems:** `pywin32` (Windows-only) in `requirements.txt` broke the Linux build; `unable to open database file` fixed with `os.makedirs()` and `create_all()`; free-tier cold starts of 30-60 seconds.

**Decision:** Demo locally; keep the Render URL for reference.

**Status:** needs checking. I have not re-verified that the Render deployment is still live, and the Streamlit dashboard is not deployed. SQLite on Render's free tier is ephemeral, so data would reset on restart.

---

# Part 2 - Audit and fixes (October 2026)

Method: for each issue I first confirmed it in the code or data, then made the smallest change, then tested it. Numbers below were measured, not estimated.

## Phase 15 - Cover letter hallucination

**Problem:** With only "python" and 1 year entered, the letter invented results ("reduced latency by 35%", "led a migration").
**Cause:** The prompt asked for something "specific and impactful" and never limited the LLM to the user's facts.
**Fix:** Rewrote the prompt: use only the given skills and years, no invented employers, numbers or results, no claims about the company, and `[placeholders]` where details are missing.
**Test:** A script runs real Groq calls and flags percentages, "10k"-style numbers, achievement verbs and fake employers. The Backend Developer case I reviewed returned 3 placeholders and no flags. LLM output varies between runs, so this is a check, not a guarantee.

## Phase 16 - Skill extraction

**Problem:** "Go" was the top skill.
**Cause:** `\bgo\b` matches the English word "go". `\b` also matched "R" in "R&D", and `C++` / `C#` could never match because `\b` does not work after a symbol.
**Fix:** One shared extractor (`skill_extractor.py`) replacing three copied versions. Ambiguous skills (go, r, ray, node, agents) need context, such as "Golang" or "Experience in Go".
**Result (number of jobs mentioning each skill, measured on the 1,559 jobs in the database at that time):**

| Skill | Before | After |
|---|---|---|
| go | 76 | 60 (spot-checked samples were real `golang` tags) |
| r | 42 | 2 |
| c++ | 0 | 40 |
| c# | 0 | 18 |

Python became the top skill. Limitation: a bare lowercase `go` tag cannot be told apart from the word, so it is ignored.

## Phase 17 - Skill matching

**Problem:** Matching was an exact set intersection, so "JS" did not match "javascript". Raw tags like "sales" and "it jobs" also polluted the skill field.
**Fix:** A synonym map (JS, sklearn, postgres, ML, k8s ...), a required vs nice-to-have split based on wording in the description, and non-skill tags ignored. The match % is still calculated in code.
**Result:** In my test, 55 of 216 Python jobs had a clear required/nice split. The rest had no such wording, so every skill counts as required. Ties are now ranked by the number of matched skills, because "100%" from 1 of 1 skills is a weak signal.

## Phase 18 - Duplicate jobs

**Problem:** The Job Browser showed "Artefact" and "Artefactlinkedin" as two jobs.
**Cause:** Dedup only checked `job_id`.
**Fix:** A duplicate key of normalized company + title + city (removes legal suffixes, "linkedin", "(m/f/d)", accents). `save_jobs` checks it, and a one-time cleanup script (dry run first) removed old duplicates.
**Result:** 24 duplicate groups, 30 rows removed, 819 -> 789 jobs.
**Found, not fixed:** 30 descriptions have broken characters (23 RemoteOK, 7 Arbeitnow). The damage is already stored.

## Phase 19 - Location filter

**Problem:** Searching "USA" returned Swiss jobs.
**Cause:** The filter was a substring match and SQLite ignores case, so "Lausanne" contains "usa".
**Fix:** Whole-word matching plus a country and city lookup (so "Germany" finds Berlin and München), US state codes, and a checkbox for worldwide-remote jobs. The API `/jobs` endpoint has the same filter.
**Limits:** The city list is hand-made. About 22 small-town jobs stayed unresolved, 54 jobs have no location and never match a place search.

## Phase 20 - Honest model evaluation

**Problem:** The sidebar showed 68.2% accuracy with no baseline.
**Finding:** On the old 1,559-job data, always guessing "other_tech" scored 70.8%, so the model was below the baseline. The data later changed (non-tech jobs removed), so I re-measured with 5 stratified train/test splits on 789 jobs:

| Input | Accuracy | Majority baseline | Macro F1 |
|---|---|---|---|
| Title + tags + description[:200] | 59.7% (+/- 3.3) | 47.5% | 0.417 |
| Title hidden | 51.9% (+/- 4.4) | 47.5% | 0.297 |

`qa_testing` had 0% recall.
**Conclusion:** The model beats the baseline but is weak. Category labels are made from title keywords, so a plain rule does the job better. I describe it as a demonstration of online learning, tracking and retraining, not a production classifier. The sidebar now shows held-out accuracy and the gap to the baseline.

**Follow-up with 1,086 jobs:** 59.6% (+/- 2.2) vs a 47.7% baseline, macro F1 0.39, title hidden 52.2%. Adding about 300 jobs changed nothing measurable (59.7% before), and the running accuracy during training flattens at roughly 55% after about 800 jobs.

## Phase 21 - Tests and CI

**Built:** 67 pytest tests (skill extractor edge cases, match %, dedup, location) and a GitHub Actions workflow. Both runs passed.
**Also fixed:** `requirements.txt` was saved as UTF-16 (a PowerShell side effect), which breaks installs on Linux and in CI. I converted it to UTF-8. Database backup files had been committed by accident, so `.gitignore` now ignores `data/database/*.db`.
**Not covered:** the resume parser and the LLM calls have no tests.

## Phase 22 - Documentation

Rewrote the README, Run Guide, Project architecture and this file. Removed claims I could not back up: "production-grade", "4 working APIs", "improves daily", spaCy and NLTK as extraction tools, and invented clock times. Added cross-platform commands, screenshots and a Limitations section.

## Phase 23 - Open problems

Found during the audit, **not fixed yet**:

- ~~The Muse returned HTTP 403~~ **Fixed (13 Oct 2026):** the API rejects Python's default user agent. Sending a `User-Agent` header fixed it. It adds few tech jobs: 19 of 100 fetched were kept after preprocessing.
- **Ingestion re-adds non-tech jobs** that preprocessing deleted: one run saved 1,041 of 1,192 fetched jobs.
- **Drift detection** flags volume changes and the reference data is never refreshed, so it can retrain on every run. The scheduler also trains and then retrains after a drift flag.
- **Resume upload** builds a temp file path from the uploaded filename without checking it, and has no size or type limit.
- **Resume parser** defaults to 1 year of experience when none is found.
- **90-day roadmap** is free text from the LLM and renders unevenly.
- **Docker and deployment** are untested.

---

## Key Lessons Learned

1. `\b` is not enough for skill matching. Short or ambiguous words (go, r) need context, and symbols (`C++`) need their own rules.
2. Never let an LLM produce numbers that code can calculate, and tell it to use only the facts you give it.
3. Variable-name conflicts are silent bugs.
4. A model's accuracy means nothing without a baseline. Always compare with "always guess the biggest class".
5. Check where labels come from. If the labels come from the input, the model is relearning a rule.
6. Do not write "improves over time" until you have measured it.
7. `pip freeze` on Windows includes Windows-only packages, and PowerShell can save files as UTF-16.
8. Free cloud tiers sleep and often have temporary disks, so SQLite data can disappear.
9. MLflow's file store is deprecated; use a database backend.
10. Test with real data. Most bugs in this audit (go, C++, "usa" in "Lausanne") only showed up on real jobs.