import sqlite3, pickle, os

def section(name):
    print("\n=== " + name + " ===")

# 1. Jobs table
try:
    section("JOBS")
    c = sqlite3.connect("data/database/careerpulse.db")
    print("total jobs:", c.execute("select count(*) from jobs").fetchone()[0])
    print("jobs per source:", c.execute("select source, count(*) from jobs group by source").fetchall())
    print("created_at range:", c.execute("select min(created_at), max(created_at) from jobs").fetchone())
    print("same title+company twice:", c.execute(
        "select count(*) from (select 1 from jobs group by lower(title), lower(company) having count(*)>1)").fetchone()[0])
    print("company names containing 'linkedin':", c.execute(
        "select company, count(*) from jobs where lower(company) like '%linkedin%' group by company limit 10").fetchall())
    print("top 10 locations:", c.execute(
        "select location, count(*) from jobs group by location order by 2 desc limit 10").fetchall())
except Exception as e:
    print("ERROR:", e)

# 2. Skills list size
try:
    section("SKILLS")
    from pipeline.skills import SKILLS_LIST
    print("skills in SKILLS_LIST:", len(SKILLS_LIST))
except Exception as e:
    print("ERROR:", e)

# 3. Model metrics
try:
    section("MODEL METRICS")
    with open("data/feature_store/model_metrics.pkl", "rb") as f:
        print(pickle.load(f))
except Exception as e:
    print("ERROR:", e)

# 4. Drift report (shortened)
try:
    section("DRIFT REPORT")
    with open("data/feature_store/drift_report.pkl", "rb") as f:
        print(str(pickle.load(f))[:800])
except Exception as e:
    print("ERROR:", e)

# 5. MLflow runs
try:
    section("MLFLOW")
    m = sqlite3.connect("data/mlflow/mlflow.db")
    print("runs:", m.execute("select count(*) from runs").fetchone()[0])
    print("experiments:", m.execute("select name from experiments").fetchall())
except Exception as e:
    print("ERROR:", e)

# 6. Last updated
try:
    section("LAST UPDATED")
    print(open("data/raw/last_updated.txt").read())
except Exception as e:
    print("ERROR:", e)

# 7. Features CSV (category distribution)
try:
    section("FEATURES CSV")
    import pandas as pd
    df = pd.read_csv("data/feature_store/jobs_features.csv")
    print("shape:", df.shape)
    print("columns:", list(df.columns)[:30])
    for col in df.columns:
        if df[col].dtype == object and df[col].nunique() <= 15:
            print(col, df[col].value_counts().to_dict())
except Exception as e:
    print("ERROR:", e)