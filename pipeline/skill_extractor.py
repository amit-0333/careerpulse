import re
from pipeline.skills import SKILLS_LIST

# Skills that are also normal English words need extra context to count.
_LEAD = r"(?:^|[,/(:;|]|\b(?i:in|with|using|and|or)\s)\s*"

AMBIGUOUS = {
    "go": [
        r"(?i:\bgolang\b)",
        r"\bGo\s+(?i:language|programming|lang)\b",
        _LEAD + r"Go(?![\w-])(?!\s+(?i:to|the|for|a|an|on|beyond|further|above|ahead|back|out|home|live|through)\b)",
    ],
    "r": [
        _LEAD + r"R(?=\s*(?:[,/);|]|$|\.(?:\s|$))|\s+(?i:and|or|programming|language|studio)\b)",
    ],
    "ray": [
        r"(?i:\bray\s+(?:serve|train|tune|core|data|cluster|rllib|framework)\b)",
    ],
        "agents": [
        r"(?i:\bllm\s+agents\b|\bagentic\b|\bagents?\s+(?:framework|workflow)s?\b)",
    ],
    "node": [
        r"(?i:\bnode\.?js\b|\bnode\s+js\b|\bnode\s+(?:developer|backend|runtime|server|framework)\b)",
    ],
}

_PLAIN = {
    s: re.compile(r"(?<![\w+#])" + re.escape(s) + r"(?![\w+#])", re.IGNORECASE)
    for s in SKILLS_LIST
    if s not in AMBIGUOUS
}
_AMBIG = {s: [re.compile(p, re.MULTILINE) for p in pats] for s, pats in AMBIGUOUS.items()}


def extract_skills_list(text):
    """Return skills found in text, as a list, in SKILLS_LIST order."""
    if not text:
        return []
    found = {s for s, rx in _PLAIN.items() if rx.search(text)}
    for s, rxs in _AMBIG.items():
        if any(rx.search(text) for rx in rxs):
            found.add(s)
    return [s for s in SKILLS_LIST if s in found]


def extract_skills(text):
    """Same as extract_skills_list, but as 'a, b, c' string."""
    return ", ".join(extract_skills_list(text))