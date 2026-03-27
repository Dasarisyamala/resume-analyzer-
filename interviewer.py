import json

with open("data/questions.json") as f:
    questions = json.load(f)

def generate_questions(skills):
    q_list = []

    for skill in skills:
        if skill in questions:
            q_list.extend(questions[skill])

    return q_list