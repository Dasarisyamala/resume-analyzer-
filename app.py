from flask import Flask, render_template, request
import os
import sqlite3
import re

# 🔹 Project modules
from parser import extract_text
from skills import extract_skills
from jobs import match_job
from interviewer import generate_questions
from database import init_db, save_resume

app = Flask(__name__)

# 📁 Upload folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 🧠 Initialize Database
init_db()


# 🏠 Home Page
@app.route("/")
def home():
    return render_template("index.html")


def extract_field(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


# 📄 Batch Resume Upload + Processing
@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        return "❌ No file uploaded"

    files = request.files.getlist("resume")
    if not files or all(f.filename.strip() == "" for f in files):
        return "❌ No file(s) selected"

    results = []
    allowed_ext = {".pdf"}

    for file in files:
        if file.filename == "":
            continue

        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in allowed_ext:
            results.append({
                "filename": file.filename,
                "error": "Unsupported file type. Please upload PDF resumes only.",
            })
            continue

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # 🧠 Step 1: Extract text
        text = extract_text(filepath)
        if not text or text.startswith("[PDF_ERROR]"):
            results.append({
                "filename": file.filename,
                "error": text or "Empty or unreadable file"
            })
            continue

        # 🧠 Step 2: Extract skills
        skills = extract_skills(text)

        # 🧠 Step 3: Job matching (ATS Score)
        job_scores = match_job(skills)

        # 🧠 Step 4: Generate interview questions
        questions = generate_questions(skills)

        # 🧠 Step 5: Extract additional fields
        name = extract_field(r"Name[:\s]*([A-Za-z .]+)", text)
        email = extract_field(r"([\w\.-]+@[\w\.-]+)", text)
        phone = extract_field(r"(\+?\d[\d\s-]{8,}\d)", text)
        education = extract_field(r"Education[:\s]*([\w\W]+?)(?:Experience|Skills|$)", text)
        experience = extract_field(r"Experience[:\s]*([\w\W]+?)(?:Education|Skills|$)", text)

        # 💾 Step 6: Save to database
        save_resume(file.filename, name, email, phone, education, experience, skills, job_scores)

        results.append({
            "filename": file.filename,
            "name": name,
            "email": email,
            "phone": phone,
            "education": education,
            "experience": experience,
            "skills": skills,
            "job_scores": job_scores,
            "questions": questions,
            "error": None
        })

    if not results:
        return "❌ No valid files processed"

    return render_template("result.html", results=results)


# 📜 History Page (Simple View)
@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resumes")
    data = cursor.fetchall()

    conn.close()

    return f"""
    <h2>📂 Resume History</h2>
    <p>{data}</p>
    <br><a href="/">⬅ Back</a>
    """


# ▶ Run App
if __name__ == "__main__":
    app.run(debug=True)