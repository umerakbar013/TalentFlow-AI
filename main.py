from fastapi import FastAPI
from pydantic import BaseModel
from agents.screening_agent import ScreeningAgent

app = FastAPI(title="TalentFlow AI Core Engine")

class ScreeningRequest(BaseModel):
    resume_text: str

class ScreeningResponse(BaseModel):
    score: float
    passed: bool
    feedback: str

@app.get("/")
def system_status():
    return {"status": "Online", "module": "TalentFlow API"}

@app.post("/api/v1/screen", response_model=ScreeningResponse)
def trigger_screening(payload: ScreeningRequest):
    """External hook to bypass UI and screen directly via API."""
    agent = ScreeningAgent(job_description="AI Engineer Python")
    result = agent.evaluate_resume(payload.resume_text)
    return ScreeningResponse(**result)