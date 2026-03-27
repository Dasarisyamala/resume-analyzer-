import json

with open("data/jobs.json") as f:
    jobs = json.load(f)

def match_job(user_skills):
    scores = {}

    for job, skills in jobs.items():
        match = len(set(user_skills) & set(skills))
        score = (match / len(skills)) * 100
        scores[job] = round(score, 2)

    return scores