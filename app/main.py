from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional  # <<<--- 1. ADDED THIS IMPORT
# Import BOTH functions from your ai.py file
from app.ai import score_resume, generate_summary


# --- Model for /score-resume ---
class ScoreRequest(BaseModel):
    job_description: str
    resume_text: str

# --- 2. ADDED THIS NEW RESPONSE MODEL ---
# This defines our new "Gemini-like" output
class ScoreResponse(BaseModel):
    Score: int
    KeyMatches: List[str]
    SkillsGap: List[str]
    summary_analysis: str
    Method: Optional[str] = None

    class Config:
        # This allows Pydantic to map fields with spaces
        # (like 'Key Matches') to our model fields (like 'KeyMatches')
        allow_population_by_field_name = True
        alias_generator = lambda x: {
            'KeyMatches': 'Key Matches',
            'SkillsGap': 'Skills Gap'
        }.get(x, x)


# --- Models for /summarize (Unchanged) ---
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str


app = FastAPI(title="FastTrack HR Agent")

# Allow the Next.js frontend (running on localhost:3000) to call this API.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 3. UPDATED THIS ENDPOINT ---
@app.post("/score-resume", response_model=ScoreResponse) # <<< Set the response_model
async def score_resume_endpoint(req: ScoreRequest):
    """Simple endpoint that returns a JSON score and matches for a resume vs job description."""
    result = score_resume(req.job_description, req.resume_text)
    
    # Pydantic will automatically validate the 'result' dictionary
    # against the 'ScoreResponse' model and handle aliases.
    return result


# --- NEW: Endpoint for /summarize (Unchanged) ---
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(request: SummarizeRequest):
    """
    New endpoint that takes a block of text and returns a concise summary.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Call the new function from ai.py
        summary = generate_summary(request.text) 
        return SummarizeResponse(summary=summary)
    except Exception as e:
        # Handle potential errors from the AI call
        print(f"Error in /summarize: {e}") # Log the error for debugging
        raise HTTPException(status_code=500, detail=str(e))