import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.llm_coach import get_matching_jobs

jobs = get_matching_jobs("JS, sklearn, postgres, ML, python", limit=5)
for j in jobs:
    print(f"{j['match_pct']}% | {j['title']} @ {j['company']}")
    print("   required:", j["required_skills"])
    print("   matched :", j["matched_skills"], "| missing:", j["missing_skills"])
    print("   nice    :", j["nice_skills"], "| nice matched:", j["nice_matched"])

all_jobs = get_matching_jobs("python", limit=100000)
with_nice = sum(1 for j in all_jobs if j["nice_skills"])
print(f"\nJobs with a nice-to-have split: {with_nice} of {len(all_jobs)}")