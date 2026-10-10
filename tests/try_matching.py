import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.skills import SKILLS_LIST
from pipeline.skill_matching import (
    SYNONYMS, normalize_skill, normalize_skills, split_required_nice, calculate_match,
)

fails = 0


def check(name, got, expected):
    global fails
    ok = got == expected
    fails += not ok
    print("PASS" if ok else "FAIL", "|", name, "" if ok else f"| got={got} expected={expected}")


bad = sorted({v for v in SYNONYMS.values() if v not in SKILLS_LIST})
check("all synonym targets exist in SKILLS_LIST", bad, [])

for raw, exp in [("JS", "javascript"), ("sklearn", "scikit-learn"), ("Postgres", "postgresql"),
                 ("ML", "machine learning"), ("  Node.js ", "node"), ("python", "python")]:
    check(f"normalize {raw!r}", normalize_skill(raw), exp)

user = ["JS", "sklearn", "postgres", "ML", "python"]
job = ["javascript", "scikit-learn", "postgresql", "machine learning", "docker"]
check("match 4/5 = 80%", calculate_match(user, job)[0], 80)
check("no overlap = 0%", calculate_match(["cobol"], job)[0], 0)
check("empty job = 0%", calculate_match(user, []), (0, [], []))
check("duplicates not double counted", calculate_match(["python", "Python"], ["python", "sql"])[0], 50)

d1 = "Requirements: Python, SQL. Nice to have: Docker, Kubernetes."
check("header split", split_required_nice(d1, ["python", "sql", "docker", "kubernetes"]),
      (["python", "sql"], ["docker", "kubernetes"]))
d2 = "You know Python. Experience with Docker is a plus."
check("inline 'is a plus'", split_required_nice(d2, ["python", "docker"]), (["python"], ["docker"]))
d3 = "We need Python and SQL."
check("no marker = all required", split_required_nice(d3, ["python", "sql"]), (["python", "sql"], []))
d4 = "Nice to have: Docker"
check("only nice -> fall back to required", split_required_nice(d4, ["docker"]), (["docker"], []))
d5 = "Python is required. Nice to have: Python"
check("in both -> required", split_required_nice(d5, ["python"]), (["python"], []))
check("empty description", split_required_nice("", ["python"]), (["python"], []))

print("\nALL PASSED" if not fails else f"\n{fails} FAILED")