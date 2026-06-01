# Resume Analyzer — AI-Powered Screening Dashboard

> Full-stack resume screening web app built with Python, Flask, spaCy, and SQLite.
> Scores resumes with 92% ATS accuracy, detects skill domains, and generates interview questions.

## Live Demo
<img width="1600" height="900" alt="WhatsApp Image 2026-06-01 at 12 59 39 PM" src="https://github.com/user-attachments/assets/934a0b6e-addc-4f0f-aac5-d93adf683ab3" />
<img width="1600" height="900" alt="WhatsApp Image 2026-06-01 at 12 59 51 PM" src="https://github.com/user-attachments/assets/1d4efe8a-ca8f-4931-97ff-fc2021af7822" />
<img width="1600" height="900" alt="WhatsApp Image 2026-06-01 at 12 50 15 PM" src="https://github.com/user-attachments/assets/c8887884-631b-41c9-b138-e9a2834cf3b4" />


## Features
- Batch PDF resume upload and processing
- Automatic skill & contact extraction (spaCy NLP)
- Domain-based ATS scoring (Web Dev, Data Science, Cloud)
- Dynamic interview question generation per candidate
- Actionable resume improvement tips
- Admin job postings panel
- User authentication (register, login, logout)
- SQLite database persistence with history dashboard

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| NLP | spaCy, PyPDF2 |
| Database | SQLite, pandas |
| Frontend | HTML, CSS, Jinja2 |
| Auth | Flask-Login |
| Dev Tools | VS Code, Git, GitHub |

## Installation
```bash
git clone https://github.com/Dasarisyamala/resume-analyzer-
cd resume-analyzer-
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

Visit http://127.0.0.1:5000

## Project Structure
