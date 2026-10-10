import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine
from pipeline.skill_extractor import _AMBIG

WORD = sys.argv[1] if len(sys.argv) > 1 else "go"
shown = 0
with Session(engine) as s:
    for j in s.query(Job).all():
        text = f"{j.description or ''} {j.tags or ''} {j.title or ''}"
        for rx in _AMBIG[WORD]:
            m = rx.search(text)
            if m:
                a, b = max(0, m.start() - 40), m.end() + 40
                print("...", text[a:b].replace("\n", " "), "...")
                shown += 1
                break
        if shown >= 15:
            break