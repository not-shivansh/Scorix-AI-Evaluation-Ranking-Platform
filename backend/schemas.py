"""
Scorix AI — Pydantic Schemas
Request/Response models for all API endpoints.
"""

from typing import List
from pydantic import BaseModel, Field


# ── Evaluate ──────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The input prompt")
    response: str = Field(..., min_length=1, description="The AI-generated response to evaluate")


class EvaluateResponse(BaseModel):
    prompt: str
    response: str
    score: float = Field(..., ge=0, le=10, description="Predicted score from 0 to 10")


# ── Rank ──────────────────────────────────────────────────

class RankRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The input prompt")
    responses: List[str] = Field(..., min_length=2, description="List of responses to rank")


class RankedItem(BaseModel):
    rank: int
    response: str
    score: float


class RankResponse(BaseModel):
    prompt: str
    ranked_responses: List[RankedItem]


# ── Feedback ──────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    score: float = Field(..., ge=0, le=10, description="User-assigned score from 0 to 10")


class FeedbackResponse(BaseModel):
    message: str
    id: int


# ── Training ─────────────────────────────────────────────

class TrainResponse(BaseModel):
    message: str
    mae: float = Field(..., description="Mean Absolute Error on test set")
    r2: float = Field(..., description="R² score on test set")
    samples_used: int
