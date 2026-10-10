import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.location import location_matches as m, countries_in, is_remote

fails = 0


def check(name, got, expected):
    global fails
    ok = got == expected
    fails += not ok
    print("PASS" if ok else "FAIL", "|", name, "" if ok else f"| got={got} expected={expected}")


check("Lausanne is NOT USA", m("Lausanne, Vaud", "USA"), False)
check("Zurich is NOT USA", m("Zurich", "USA"), False)
check("New York, NY is USA", m("New York, NY", "USA"), True)
check("San Francisco, CA matches 'us'", m("San Francisco, CA", "us"), True)
check("Springfield, IL (state code) is USA", m("Springfield, IL", "USA"), True)
check("Remote - US matches USA", m("Remote - US", "USA"), True)
check("plain Remote matches USA (include_remote)", m("Remote", "USA"), True)
check("plain Remote hidden when include_remote off", m("Remote", "USA", include_remote=False), False)
check("Remote - US not India", m("Remote - US", "India", include_remote=True), False)
check("empty location + job_type remote matches USA", m("", "USA", job_type="remote"), True)
check("Berlin + job_type remote not USA", m("Berlin", "USA", job_type="remote"), False)
check("Bangalore, Karnataka is India", m("Bangalore, Karnataka", "India"), True)
check("UK - London matches UK", m("UK - London", "UK"), True)
check("London matches 'United Kingdom'", m("London", "United Kingdom"), True)
check("Berlin matches Germany", m("Berlin", "Germany"), True)
check("Berlin matches 'ber' (prefix)", m("Berlin", "ber"), True)
check("'usa' never matches Lausanne as text", m("Lausanne", "usa"), False)
check("query remote -> Remote job", m("Remote", "remote"), True)
check("query remote -> Berlin job", m("Berlin", "remote"), False)
check("query remote -> job_type remote", m("Berlin", "remote", job_type="remote"), True)
check("empty location never matches a place", m("", "USA"), False)
check("empty query matches all", m("Berlin", ""), True)
check("countries_in Lausanne", countries_in("Lausanne, Vaud"), {"ch"})
check("is_remote Remote", is_remote("Remote"), True)

print("\nALL PASSED" if not fails else f"\n{fails} FAILED")

# Real data report (read-only)
try:
    from sqlalchemy.orm import Session
    from pipeline.ingestion import Job, engine
    with Session(engine) as s:
        jobs = s.query(Job).all()
    for q in ["USA", "India", "Germany", "remote"]:
        hits = [j for j in jobs if m(j.location, q, j.job_type)]
        print(f"\nquery {q!r}: {len(hits)} of {len(jobs)} jobs")
        print("  sample locations:", Counter(j.location for j in hits).most_common(8))
    unresolved = Counter(
        j.location for j in jobs
        if j.location and not countries_in(j.location) and not is_remote(j.location, j.job_type)
    )
    print("\nUNRESOLVED locations (no country found):", sum(unresolved.values()), "jobs")
    print(unresolved.most_common(25))
    print("EMPTY locations:", sum(1 for j in jobs if not j.location))
except Exception as e:
    print("DB part skipped:", e)