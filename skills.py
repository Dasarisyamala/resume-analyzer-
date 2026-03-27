import pandas as pd
import spacy

nlp = spacy.load("en_core_web_sm")

# Load dataset
skills_df = pd.read_csv("data/skills.csv")
skills_list = skills_df["skill"].tolist()

def extract_skills(text):
    doc = nlp(text.lower())
    found = []

    for token in doc:
        if token.text in skills_list:
            found.append(token.text)

    return list(set(found))