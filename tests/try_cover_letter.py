import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.llm_coach import generate_cover_letter

CASES = [
    ("ML Engineer", "Artefact", "python", 1),
    ("Data Analyst", "Zalando", "python, sql", 0),
    ("Backend Developer", "Stripe", "python, fastapi, docker", 2),
]

# Patterns that usually mean the model invented something
SUSPICIOUS = [
    (r"\d+\s*%", "percentage"),
    (r"\b\d[\d,\.]*\s*(k|m)\b", "big number (10k, 2m)"),
    (r"requests? per second|\brps\b|\bqps\b", "performance claim"),
    (r"\b(led|reduced|improved|increased|migrated|scaled|spearheaded)\b", "achievement verb"),
    (r"\b(at|with)\s+(xyz|acme|abc)\b", "fake employer"),
    (r"\b(your|the company's)\s+(mission|culture|values)\b", "company claim"),
]

for title, company, skills, years in CASES:
    print("=" * 70)
    print(f"INPUT: {title} @ {company} | skills: {skills} | years: {years}")
    print("=" * 70)
    letter = generate_cover_letter(title, company, skills, years)
    print(letter)
    print("-" * 70)
    flags = []
    for pattern, label in SUSPICIOUS:
        for m in re.finditer(pattern, letter, flags=re.IGNORECASE):
            flags.append(f"{label}: '{m.group(0)}'")
    placeholders = re.findall(r"\[[^\]]+\]", letter)
    print("PLACEHOLDERS FOUND:", len(placeholders))
    print("SUSPICIOUS FLAGS:", flags if flags else "none")
    print("WORD COUNT:", len(letter.split()))