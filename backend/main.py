"""
Scorix AI — FastAPI Backend
All API endpoints for evaluation, ranking, feedback, and training.
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import init_db, get_db, Feedback, EvaluationLog
from backend.schemas import (
    EvaluateRequest, EvaluateResponse,
    RankRequest, RankResponse, RankedItem,
    FeedbackRequest, FeedbackResponse,
    TrainResponse,
)
from backend.model import predict_score, load_model, train_model


# ── App Setup ─────────────────────────────────────────────

app = FastAPI(
    title="Scorix AI",
    description="ML-based AI Evaluation & Ranking Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

# Try to load ML model on startup
try:
    load_model()
    print("[OK] BERT model loaded successfully.")
except Exception:
    print("[WARN] BERT model not found. Train a model first via /upload-dataset or train_bert.py.")

# ── Paths ─────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── API Endpoints ─────────────────────────────────────────

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Scorix AI"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest, db: Session = Depends(get_db)):
    """Score a single AI-generated response."""
    try:
        score = predict_score(request.prompt, request.response)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # Log evaluation
    log = EvaluationLog(
        prompt=request.prompt,
        response=request.response,
        predicted_score=score,
    )
    db.add(log)
    db.commit()

    return EvaluateResponse(
        prompt=request.prompt,
        response=request.response,
        score=score,
    )


@app.post("/rank", response_model=RankResponse)
def rank(request: RankRequest, db: Session = Depends(get_db)):
    """Score and rank multiple responses for a given prompt."""
    scored = []
    for resp in request.responses:
        try:
            score = predict_score(request.prompt, resp)
        except RuntimeError as e:
            raise HTTPException(status_code=503, detail=str(e))

        # Log each evaluation
        log = EvaluationLog(
            prompt=request.prompt,
            response=resp,
            predicted_score=score,
        )
        db.add(log)
        scored.append({"response": resp, "score": score})

    db.commit()

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    ranked = [
        RankedItem(rank=i + 1, response=item["response"], score=item["score"])
        for i, item in enumerate(scored)
    ]

    return RankResponse(prompt=request.prompt, ranked_responses=ranked)


@app.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest, db: Session = Depends(get_db)):
    """Store user feedback for model improvement."""
    feedback = Feedback(
        prompt=request.prompt,
        response=request.response,
        score=request.score,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse(
        message="Feedback saved successfully",
        id=feedback.id,
    )


@app.post("/upload-dataset", response_model=TrainResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV dataset and retrain the BERT model."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    # Save uploaded file
    os.makedirs(DATA_DIR, exist_ok=True)
    upload_path = os.path.join(DATA_DIR, "uploaded_dataset.csv")

    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Retrain model
    try:
        metrics = train_model(upload_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Training failed: {str(e)}")

    return TrainResponse(
        message="Model retrained successfully",
        mae=metrics["mae"],
        r2=metrics["r2"],
        samples_used=metrics["samples_used"],
    )


# ── Static Files (Frontend) ──────────────────────────────

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
