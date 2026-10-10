"""One-time cleanup of duplicate jobs already in the database.

Dry run (changes nothing):   python -m pipeline.dedup_cleanup
Really delete duplicates:    python -m pipeline.dedup_cleanup --apply
"""
import sys
from collections import defaultdict
from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine
from pipeline.dedup import dedup_key


def find_duplicate_groups(jobs):
    groups = defaultdict(list)
    for j in jobs:
        key = dedup_key(j.company, j.title, j.location)
        if key is not None:
            groups[key].append(j)
    return [g for g in groups.values() if len(g) > 1]


def pick_keeper(group):
    # keep the job with the longest description; on a tie keep the oldest row
    return max(group, key=lambda j: (len(j.description or ""), -j.id))


def cleanup(apply=False):
    with Session(engine) as session:
        jobs = session.query(Job).all()
        groups = find_duplicate_groups(jobs)
        to_delete = []
        for g in groups:
            keeper = pick_keeper(g)
            to_delete.extend(j for j in g if j.id != keeper.id)
        print(f"Jobs in DB: {len(jobs)}")
        print(f"Duplicate groups: {len(groups)} | rows to delete: {len(to_delete)}")
        for g in groups[:10]:
            print("  -", [(j.source, j.company, j.title, j.location) for j in g])
        if apply:
            for j in to_delete:
                session.delete(j)
            session.commit()
            print(f"[DONE] Deleted {len(to_delete)} duplicate rows. Jobs left: {len(jobs) - len(to_delete)}")
        else:
            print("[DRY RUN] Nothing changed. Add --apply to delete.")


if __name__ == "__main__":
    cleanup(apply="--apply" in sys.argv)