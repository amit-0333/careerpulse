import pytest
from pipeline.skill_extractor import extract_skills_list

CASES = [
    ("We want you to go the extra mile", "go", False),
    ("Let's go build things", "go", False),
    ("Go to market strategy", "go", False),
    ("Experience in Go or Rust", "go", True),
    ("Backend services in Golang", "go", True),
    ("Skills: Go, Python", "go", True),
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


@pytest.mark.parametrize("text,skill,expected", CASES)
def test_skill_detection(text, skill, expected):
    assert (skill in extract_skills_list(text)) == expected


def test_empty_text_gives_no_skills():
    assert extract_skills_list("") == []
    assert extract_skills_list(None) == []