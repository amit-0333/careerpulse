import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.skill_extractor import extract_skills_list

CASES = [
    ("We want you to go the extra mile", "go", False),
    ("Let's go build things", "go", False),
    ("Experience in Go or Rust", "go", True),
    ("Backend services in Golang", "go", True),
    ("Skills: Go, Python", "go", True),
    ("Go to market strategy", "go", False),
    ("R&D team, you will go far", "r", False),
    ("Skills: R, Python", "r", True),
    ("Statistics in R and SQL", "r", True),
    ("We need C++ developers", "c++", True),
    ("Experience with C# and .NET", "c#", True),
    ("JavaScript developer", "java", False),
    ("JavaScript developer", "javascript", True),
    ("Java developer", "java", True),
    ("insurance agents wanted", "agents", False),
    ("build LLM agents", "agents", True),
    ("Ray Ban sunglasses", "ray", False),
    ("distributed training with Ray Train", "ray", True),
    ("edge node of the network", "node", False),
    ("Node.js backend", "node", True),
    ("Apache Spark pipelines", "apache spark", True),
]

bad = 0
for text, skill, expected in CASES:
    got = skill in extract_skills_list(text)
    ok = got == expected
    bad += not ok
    print(("PASS" if ok else "FAIL"), f"| {skill!r:14} expected={expected!s:5} | {text}")
print(f"\n{len(CASES) - bad}/{len(CASES)} passed")

try:
    from sqlalchemy.orm import Session
    from pipeline.ingestion import Job, engine

    old, new = Counter(), Counter()
    with Session(engine) as s:
        jobs = s.query(Job).all()
    for j in jobs:
        for t in (j.tags or "").split(","):
            if t.strip():
                old[t.strip().lower()] += 1
        text = f"{j.description or ''} {j.tags or ''} {j.title or ''}"
        for sk in extract_skills_list(text):
            new[sk] += 1
    print(f"\nJobs: {len(jobs)}")
    print("OLD top 10 (stored tags):", old.most_common(10))
    print("NEW top 10:              ", new.most_common(10))
    print("go: old =", old.get("go", 0), "| new =", new.get("go", 0))
    print("r: old =", old.get("r", 0), "| new =", new.get("r", 0))
    print("c++: old =", old.get("c++", 0), "| new =", new.get("c++", 0))
    print("c#: old =", old.get("c#", 0), "| new =", new.get("c#", 0))
except Exception as e:
    print("DB part skipped:", e)