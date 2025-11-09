import os
import re
import json
from collections import Counter
from typing import Dict, Any, List

# --- Imports for the new Chat-based OpenAI call ---
try:
    import openai
except ImportError:
    print("OpenAI not installed. LLM features will be disabled.")
    openai = None

# --- ENHANCEMENT 1: ADD WEAK KEYWORDS TO EXCLUDE NON-SKILLS ---
WEAK_KEYWORDS = {
    "need", "required", "experience", "work", "engineer", "software",
    "developer", "team", "project", "building", "design", "skills",
    "knowledge", "ability", "etc", "years", "role", "must", "bachelor"
}

STOPWORDS = {
    "the", "and", "to", "of", "a", "in", "for", "with", "on", "is", 
    "that", "as", "are", 
}


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9#+.-_]+", text.lower())
    return [w for w in words if w 
            and w not in STOPWORDS 
            and w not in WEAK_KEYWORDS
            and len(w) > 1]


def extract_keywords(text: str, top_n: int = 12) -> List[str]:
    tokens = _tokenize(text)
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


def _keyword_score(jd: str, resume: str) -> Dict[str, Any]:
    keywords = extract_keywords(jd, top_n=12)
    matches = [k for k in keywords if re.search(r"\b" + re.escape(k) + r"\b", resume, re.I)]
    
    score = 1
    if keywords:
        score = int(round(len(matches) / len(keywords) * 9)) + 1
        score = max(1, min(10, score))

    # This is the fallback response if the LLM fails
    return {
        "Score": score,
        "Key Matches": matches,
        "Skills Gap": [k for k in keywords if k not in matches],
        "summary_analysis": "This is a basic keyword match. The AI analysis (LLM) is either disabled or failed. Please check your OPENAI_API_KEY."
    }

def generate_summary(text: str) -> str:
    """
    Generates a concise summary of the input text using an LLM.
    """
    use_llm = os.getenv("USE_LLM", "0") == "1"
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not use_llm or not openai or not api_key:
        sentences = text.split('.')
        fallback_summary = ". ".join(sentences[:3]).strip()
        if len(sentences) > 3: fallback_summary += "..."
        return f"(LLM Misconfigured) Fallback: {fallback_summary}"

    try:
        openai.api_key = api_key
        
        # Using ChatCompletion for a "smarter" summary
        messages = [
            {"role": "system", "content": "You are an expert HR analyst. Summarize the following text (job description or resume) into concise bullet points, focusing on key skills, technologies, and experience levels."},
            {"role": "user", "content": text}
        ]

        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.1,
            max_tokens=200,
        )
        summary_text = response.choices[0].message['content'].strip()
        return summary_text
        
    except Exception as e:
        print(f"Error during summarization: {e}")
        return f"(API Error) Could not summarize text."

def score_resume(jd: str, resume: str) -> Dict[str, Any]:
    """
    Primary integration function. Tries to call an LLM if configured,
    otherwise returns a deterministic keyword overlap score.
    """
    use_llm = os.getenv("USE_LLM", "0") == "1"
    api_key = os.getenv("OPENAI_API_KEY") # Corrected way to get key
    
    if not use_llm or not openai or not api_key:
        return _keyword_score(jd, resume) # Fallback to keyword method

    try:
        openai.api_key = api_key

        # --- THIS IS THE NEW "GEMINI-LIKE" PROMPT ---
        # We are asking for a new 'summary_analysis' field.
        system_prompt = (
            "You are an expert HR screener. Given a job description and a resume, "
            "provide a strict, valid JSON object with the following fields:\n"
            "- 'Score': An integer from 1-10, rating the resume's fit for the job.\n"
            "- 'Key Matches': An array of strings listing key skills from the JD that ARE present in the resume.\n"
            "- 'Skills Gap': An array of strings listing key skills from the JD that ARE NOT present in the resume.\n"
            "- 'summary_analysis': A 2-3 sentence professional analysis explaining the 'Score'. "
            "Describe *why* the candidate is (or isn't) a good fit, like you're talking to a hiring manager."
        )
        
        user_prompt = (
            "Job Description:\n" + jd + "\n\nResume:\n" + resume + "\n\nJSON:"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # --- USING THE NEW CHATCOMPLETION API ---
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.0,
            max_tokens=1024,
            # NEW: Force JSON output mode if available (for supported models)
            response_format={ "type": "json_object" } 
        )
        
        text = response.choices[0].message['content'].strip()
        
        # Naive extraction: find first JSON-like substring
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            parsed = json.loads(m.group(0))
            parsed["Method"] = "llm (gpt-3.5-turbo)"
            
            # Ensure all keys are present
            if 'summary_analysis' not in parsed:
                parsed['summary_analysis'] = "LLM did not provide a summary analysis."
            if 'Key Matches' not in parsed:
                parsed['Key Matches'] = []
            if 'Skills Gap' not in parsed:
                parsed['Skills Gap'] = []
            if 'Score' not in parsed:
                parsed['Score'] = 0
                
            return parsed
        else:
            # Fallback if JSON parsing fails
            print(f"Failed to parse JSON from LLM response: {text}")
            return _keyword_score(jd, resume)

    except Exception as e:
        print(f"Error in score_resume LLM call: {e}")
        # Fallback to keyword method if LLM fails
        return _keyword_score(jd, resume)