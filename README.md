Resume Analyzer – Backend (FastAPI)

This is the backend service for the Resume Analyzer application.
It exposes REST endpoints to:

Score resumes

Summarize resumes

Perform AI-based NLP tasks

Built using FastAPI with a modular structure.

Tech Stack

FastAPI

Python

Uvicorn

Transformers / NLP models (if used)

Project Structure
backend/
  app/
    main.py        → API endpoints
    ai.py          → NLP/AI logic
  requirements.txt
  Dockerfile

Setup Instructions
1. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

2. Install Dependencies
pip install -r requirements.txt

3. Run FastAPI Server
uvicorn app.main:app --reload --port 8000


API will run at:

http://localhost:8000

API Endpoints
Method	Endpoint	Description
POST	/score-resume	Returns score for resume
POST	/summarize	Generates summary

(Modify according to your actual endpoints if needed)

Deployment
✅ Render (Docker) – Recommended

Push repo to GitHub

Create new Web Service in Render

Select Docker Build

Set PORT=8000

✅ Local Docker
docker build -t resume-backend .
docker run -p 8000:8000 resume-backend

Environment Variables

Add in Render:

Variable	Description
API_KEY (optional)	API key for AI model (if used)
Any other secrets	Do NOT commit them to repo
License

This project is for educational and personal use.