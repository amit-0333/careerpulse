import pytest
from pipeline.skills import SKILLS_LIST
from pipeline.skill_matching import (
    SYNONYMS, normalize_skill, split_required_nice, calculate_match,
)


def test_all_synonym_targets_exist():
    assert sorted({v for v in SYNONYMS.values() if v not in SKILLS_LIST}) == []


@pytest.mark.parametrize("raw,expected", [
    ("JS", "javascript"), ("sklearn", "scikit-learn"), ("Postgres", "postgresql"),
    ("ML", "machine learning"), ("  Node.js ", "node"), ("python", "python"),
])
def test_normalize_skill(raw, expected):
    assert normalize_skill(raw) == expected


USER = ["JS", "sklearn", "postgres", "ML", "python"]
JOB = ["javascript", "scikit-learn", "postgresql", "machine learning", "docker"]


def test_match_percentage_is_computed_by_code():
    pct, matched, missing = calculate_match(USER, JOB)
    assert pct == 80
    assert missing == ["docker"]
    assert len(matched) == 4


def test_no_overlap_is_zero():
    assert calculate_match(["cobol"], JOB)[0] == 0


def test_empty_job_skills():
    assert calculate_match(USER, []) == (0, [], [])


def test_duplicates_not_double_counted():
    assert calculate_match(["python", "Python"], ["python", "sql"])[0] == 50


def test_header_split():
    d = "Requirements: Python, SQL. Nice to have: Docker, Kubernetes."
    assert split_required_nice(d, ["python", "sql", "docker", "kubernetes"]) == (
        ["python", "sql"], ["docker", "kubernetes"])


def test_inline_plus_marker():
    d = "You know Python. Experience with Docker is a plus."
    assert split_required_nice(d, ["python", "docker"]) == (["python"], ["docker"])


def test_no_marker_means_all_required():
    assert split_required_nice("We need Python and SQL.", ["python", "sql"]) == (["python", "sql"], [])


def test_only_nice_falls_back_to_required():
    assert split_required_nice("Nice to have: Docker", ["docker"]) == (["docker"], [])


def test_skill_in_both_parts_is_required():
    assert split_required_nice("Python is required. Nice to have: Python", ["python"]) == (["python"], [])