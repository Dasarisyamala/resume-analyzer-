import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    expected_columns = [
        "id",
        "filename",
        "name",
        "email",
        "phone",
        "education",
        "experience",
        "skills",
        "job_scores"
    ]

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        education TEXT,
        experience TEXT,
        skills TEXT,
        job_scores TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(resumes)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if existing_columns and existing_columns != expected_columns:
        cursor.execute("DROP TABLE IF EXISTS resumes")
        cursor.execute("""
        CREATE TABLE resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            name TEXT,
            email TEXT,
            phone TEXT,
            education TEXT,
            experience TEXT,
            skills TEXT,
            job_scores TEXT
        )
        """)

    conn.commit()
    conn.close()


def save_resume(filename, name, email, phone, education, experience, skills, job_scores):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO resumes (filename, name, email, phone, education, experience, skills, job_scores) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (filename, name, email, phone, education, experience, str(skills), str(job_scores))
    )

    conn.commit()
    conn.close()