## Resume Analysis Dashboard

This project is a lightweight Flask backend that ingests multiple PDF resumes at a time, extracts skills with spaCy + pandas, scores them against a small job dataset, generates interview questions, and persists the structured info to SQLite for HR review.

The focus is on keeping the workflow realistic for recruiters:
- Drag-and-drop batch upload (UI form posts to `/upload`).
- Automatic text extraction, skill detection, and ATS-style job matching.
- Interview question suggestions based on detected skills.
- History endpoint to review previously processed resumes.
- Friendly error handling for corrupt files or wrong formats.

---

### Project Structure

```
├── app.py             # Flask routes and batch processing logic
├── parser.py          # PDF text extraction helper (PyPDF2)
├── skills.py          # spaCy + CSV-based skill extractor
├── jobs.py            # Matches skills against data/jobs.json
├── interviewer.py     # Generates interview questions from data/questions.json
├── database.py        # SQLite helpers (init + insert)
├── templates/         # index + results dashboard
├── data/              # jobs.json, questions.json, skills.csv
└── uploads/           # Uploaded PDFs (gitignored)
```

---

### Features

- **Batch uploads**: send one or many PDF resumes and receive per-file insights.
- **Skill mining**: spaCy tokenization compared to `data/skills.csv`.
- **Job scoring**: fast overlap-based ATS score using `data/jobs.json`.
- **Interview kit**: lookup `data/questions.json` per detected skill.
- **Database persistence**: each run is inserted into SQLite (`database.db`).
- **Error feedback**: invalid filetypes (e.g., JPG) or corrupt PDFs display inline errors instead of killing the server.
- **Authentication**: users register, log in, and access protected dashboards with logout support.

---

### Requirements

- Python 3.11+
- spaCy English model `en_core_web_sm`
- Packages inside `requirements.txt` (Flask, PyPDF2, pandas, python-dotenv, etc.)

Install everything with:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

### Environment

The app runs fine with defaults (local SQLite + uploads folder). If you need to override paths, create an `.env` file:

```
UPLOAD_FOLDER=uploads
DATABASE_URL=sqlite:///database.db  # optional; current code uses sqlite3 directly
SECRET_KEY=choose-a-strong-value
```

---

### Running Locally

```bash
flask --app app run --debug
# or
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000). Upload only PDF resumes; all other formats will be rejected politely.

---

### Usage Flow

0. Hit `/register` to create an account (or `/login` if you already have one).
1. Open `/` and choose one or more PDF resumes.
2. Submit to `/upload`.
3. For each resume you’ll receive:
   - Extracted skills
   - ATS score per job profile
   - Suggested interview questions
   - Metadata (name, email, phone, experience, education when patterns are found)
   - Error card if the file was unreadable
4. Processed entries are stored in SQLite; open `/history` for a raw view.

---

### Troubleshooting

- **“Unsupported file type”**: upload PDFs only. Convert DOC/DOCX first.
- **spaCy model missing**: run `python -m spacy download en_core_web_sm`.
- **Database column errors**: delete `database.db` to let `init_db()` recreate the latest schema.
- **PyPDF2 PdfReadError**: the PDF is corrupted; re-export the resume or scan it again.

---

### Ideas & Future Work

- Use docx2txt / pdfplumber to support DOCX & scanned PDFs.
- Add richer parsing (name/email detection via regex already started).
- Build a richer `/history` page or export to CSV.
- Swap simple overlap scoring with embeddings or OpenAI functions for semantic ranking.

PRs / suggestions welcome!
