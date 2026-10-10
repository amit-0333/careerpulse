import re
from pipeline.skills import SKILLS_LIST
from pipeline.skill_extractor import extract_skills_list

# Maps what users type -> the canonical name used in SKILLS_LIST
SYNONYMS = {
    "js": "javascript", "java script": "javascript", "ts": "typescript",
    "sklearn": "scikit-learn", "scikit learn": "scikit-learn", "sci-kit learn": "scikit-learn",
    "postgres": "postgresql", "postgre sql": "postgresql", "psql": "postgresql",
    "mongo": "mongodb", "ml": "machine learning", "dl": "deep learning",
    "natural language processing": "nlp", "ai agent": "ai agents",
    "k8s": "kubernetes", "tf": "tensorflow", "torch": "pytorch", "py torch": "pytorch",
    "hugging face": "huggingface", "llama index": "llamaindex", "lang chain": "langchain",
    "node.js": "node", "nodejs": "node", "node js": "node",
    "react.js": "react", "reactjs": "react", "vue.js": "vue", "vuejs": "vue",
    "angularjs": "angular", "golang": "go", "cpp": "c++", "c sharp": "c#",
    "gen ai": "generative ai", "genai": "generative ai",
    "large language model": "llm", "large language models": "llm", "llms": "llm",
    "powerbi": "power bi", "power-bi": "power bi",
    "github action": "github actions", "gh actions": "github actions",
    "amazon web services": "aws", "google cloud platform": "gcp",
    "ci cd": "ci/cd", "cicd": "ci/cd", "ci-cd": "ci/cd",
    "bq": "bigquery", "ab testing": "a/b testing", "a b testing": "a/b testing",
    "spark": "apache spark", "pyspark": "apache spark",
    "kafka": "apache kafka", "airflow": "apache airflow", "flink": "apache flink",
    "iceberg": "apache iceberg", "sagemaker": "aws sagemaker",
    "vertex ai": "google vertex ai", "weights & biases": "weights and biases",
    "rest": "rest api", "restful": "rest api", "restful api": "rest api", "rest apis": "rest api",
    "stats": "statistics", "bi": "business intelligence",
}

# Header-style phrases: everything AFTER them is "nice to have"
_HEADER_RX = re.compile(
    r"nice[\s-]to[\s-]have|good[\s-]to[\s-]have|preferred (?:qualifications|skills|experience)"
    r"|bonus points?|bonus skills|desirable",
    re.IGNORECASE,
)
# Inline phrases: only the SENTENCE containing them is "nice to have"
_INLINE_RX = re.compile(
    r"(?:is|are)\s+(?:a\s+)?(?:plus|bonus|advantage)|\ba plus\b|would be (?:a )?(?:plus|great|nice)"
    r"|\bbonus\b|\bnice to have\b",
    re.IGNORECASE,
)


def normalize_skill(skill):
    s = re.sub(r"\s+", " ", str(skill).strip().lower())
    return SYNONYMS.get(s, s)


def normalize_skills(skills):
    """Normalize, drop empties and duplicates, keep the original order."""
    seen, out = set(), []
    for raw in skills:
        s = normalize_skill(raw)
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def split_required_nice(description, skills):
    """Split a job's skills into (required, nice_to_have) using its description.
    If the text gives no clear signal, every skill stays required."""
    text = description or ""
    if not text or not skills:
        return list(skills), []
    m = _HEADER_RX.search(text)
    head, tail = (text[:m.start()], text[m.start():]) if m else (text, "")
    nice_found = set(extract_skills_list(tail))
    required_found = set()
    for sentence in re.split(r"(?<=[.!?;])\s+", head):
        found = extract_skills_list(sentence)
        if _INLINE_RX.search(sentence):
            nice_found.update(found)
        else:
            required_found.update(found)
    nice = [s for s in skills if s in nice_found and s not in required_found]
    required = [s for s in skills if s not in nice]
    if not required:
        return list(skills), []
    return required, nice


def calculate_match(user_skills, job_required_skills):
    """Match % is computed here, in code. Returns (pct, matched, missing)."""
    user = set(normalize_skills(user_skills))
    required = normalize_skills(job_required_skills)
    if not required:
        return 0, [], []
    matched = [s for s in required if s in user]
    missing = [s for s in required if s not in user]
    return round(len(matched) / len(required) * 100), matched, missing