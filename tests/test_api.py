from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_score_resume_keyword():
    payload = {
        "job_description": "We need a python developer with experience in fastapi, docker, and testing.",
        "resume_text": "Experienced Python developer. Worked with Docker and unit testing."
    }
    r = client.post("/score-resume", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "Score" in data
    assert "Key Matches" in data
