import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pipeline.ingestion import Job, engine
from pipeline.skills import SKILLS_LIST
from pipeline.skill_matching import (
    normalize_skills, split_required_nice, calculate_match,
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"

def extract_required_skills(job_tags):
    if not job_tags:
        return []
    return [s.strip().lower() for s in job_tags.split(",") if s.strip()]

def calculate_match(user_skills_list, job_skills_list):
    if not job_skills_list:
        return 0, [], []
    user_set = set(user_skills_list)
    job_set = set(job_skills_list)
    matched = user_set & job_set
    missing = job_set - user_set
    match_pct = round((len(matched) / len(job_set)) * 100)
    return match_pct, list(matched), list(missing)

_KNOWN_SKILLS = set(SKILLS_LIST)

def extract_required_skills(job_tags):
    """Job skills only. Ignores non-skill tags like 'sales' or 'it jobs'."""
    return [s for s in normalize_skills((job_tags or "").split(","))
            if s in _KNOWN_SKILLS]

def get_matching_jobs(skills, limit=10):
    user_skills_list = normalize_skills(skills.split(","))
    user_set = set(user_skills_list)
    with Session(engine) as session:
        jobs = session.query(Job).all()
        results = []
        for job in jobs:
            job_skills_list = extract_required_skills(job.tags)
            if not job_skills_list:
                continue
            required, nice = split_required_nice(job.description, job_skills_list)
            match_pct, matched_skills, missing_skills = calculate_match(
                user_skills_list, required
            )
            results.append({
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "tags": job.tags,
                "apply_url": job.apply_url,
                "match_pct": match_pct,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "required_skills": required,
                "nice_skills": nice,
                "nice_matched": [s for s in nice if s in user_set],
            })
            results = sorted(
            results,
            key=lambda x: (x["match_pct"], len(x["matched_skills"])),
            reverse=True,
        )
        non_zero = [j for j in results if j["match_pct"] > 0]
        if len(non_zero) >= 5:
            return non_zero[:limit]
        return results[:limit]

def ask_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": GROQ_MODEL,
        "max_tokens": 2048,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=body)
    data = response.json()
    if "choices" not in data:
        print(f"[ERROR] LLM Error: {data}")
        return "LLM response failed"
    content = data["choices"][0]["message"]["content"]
    if not content:
        print(f"[ERROR] Empty response from LLM")
        return "Empty response"
    return content

def analyze_career(target_role, current_skills, experience_years):
    print("[INFO] Calculating real match scores from database...")
    matching_jobs = get_matching_jobs(current_skills, limit=10)

    jobs_text = "\n".join([
        f"- {j['title']} at {j['company']} ({j['location']}) | "
        f"Real Match: {j['match_pct']}% | "
        f"Matched Skills: {', '.join(j['matched_skills']) or 'none'} | "
        f"Missing Skills: {', '.join(j['missing_skills']) or 'none'}"
        for j in matching_jobs
    ])

    all_missing = []
    for j in matching_jobs[:5]:
        all_missing.extend(j["missing_skills"])
    top_missing = list(set(all_missing))[:10]

    prompt = f"""
You are an expert career coach for tech and data science roles.

User Profile:
- Target Role: {target_role}
- Current Skills: {current_skills}
- Years of Experience: {experience_years}

IMPORTANT: The match percentages below are REAL calculated scores
based on actual skill comparison algorithm. Do NOT change or estimate
these percentages. Use them exactly as provided.

Real Job Matches from Database:
{jobs_text}

Algorithmically detected skill gaps: {', '.join(top_missing)}

Please provide:

1. READINESS ASSESSMENT
Based on the real match scores above, how ready is this person?
Use the actual percentages provided, do not invent new ones.
If all scores are 0% say the user needs to add more relevant skills.

2. APPLY NOW
List top 3 jobs with highest real match % from the data above.
Show their exact match % as calculated.
If all are 0% suggest what skills to add to get matches.

3. NOT READY YET
List 2-3 jobs with low match % and explain exactly which skills are missing.

4. SKILL GAPS
Based on the missing skills detected above, what should they learn?

5. 90 DAY LEARNING ROADMAP
Week by week plan to fill the detected skill gaps.

6. QUICK WIN
One specific thing they can do this week.

Keep response practical and use only the real data provided above.
"""
    print("[INFO] Sending real match data to LLM...")
    response = ask_llm(prompt)
    return response, matching_jobs

def generate_cover_letter(job_title, company, user_skills, experience_years):
    prompt = f"""
Write a cover letter for the job below, using ONLY the facts I give you.

FACTS (the only things you may state as true):
- Job title: {job_title}
- Company name: {company}
- My skills: {user_skills}
- My years of professional experience: {experience_years}

RULES:
1. Mention only the skills listed above. Do not add any other skill or tool.
2. State the years of experience exactly as given. Do not round it up or call it "extensive".
3. Do NOT invent anything: no past employers, projects, achievements,
   numbers, percentages, metrics, team sizes, awards or degrees.
4. If a detail would make the letter stronger but is not in the facts,
   write a clear placeholder in square brackets instead, for example:
   [add one project where you used Python] or [add a result you achieved, with a real number].
   Include 2 or 3 such placeholders.
5. You know nothing about {company} except its name. Do not describe its
   products, mission, culture, news or technology. Where you would say why
   you like the company, write [add why you want to join {company}].
6. Write in first person, in a plain and honest tone, under 250 words.
7. Do not start with "I am writing to express my interest".
8. Do not use the words "led", "reduced", "improved", "increased", "migrated"
   or "scaled" unless they describe something in the facts above.
"""
    print("[INFO] Generating cover letter...")
    return ask_llm(prompt)

def get_interview_questions(job_title, user_skills):
    prompt = f"""
Generate 8 likely interview questions for a {job_title} role
for someone with these skills: {user_skills}

Include:
- 3 technical questions
- 2 behavioral questions
- 2 system design questions
- 1 tricky question they might not expect

For each question also give a brief tip on how to answer it.
"""
    print("[INFO] Generating interview questions...")
    return ask_llm(prompt)

if __name__ == "__main__":
    print("[INFO] LLM Career Coach Started")

    response, jobs = analyze_career(
        target_role="ML Engineer",
        current_skills="python, pandas, scikit-learn, sql",
        experience_years=1
    )

    print("\n[LLM CAREER COACH RESPONSE]")
    print(response)

    print("\n[INFO] Top matching jobs:")
    for job in jobs[:5]:
        print(f"  {job['match_pct']}% | {job['title']} at {job['company']} | Missing: {', '.join(job['missing_skills'][:3])}")