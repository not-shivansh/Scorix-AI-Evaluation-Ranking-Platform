"""
Scorix AI — TF-IDF + Feature Engineered Scoring Model
High-performance version for better R²
"""

import os
import pickle
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# PATHS
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(DATA_DIR, "vectorizer.pkl")

# ---------------------------
# GLOBALS
# ---------------------------
_model = None
_vectorizer = None


# ---------------------------
# LOAD MODEL
# ---------------------------
def _load():
    global _model, _vectorizer

    if _model is not None and _vectorizer is not None:
        return True

    if not os.path.exists(MODEL_PATH):
        return False

    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        _vectorizer = pickle.load(f)

    return True


def load_model():
    return _load()


# ---------------------------
# FEATURE ENGINEERING
# ---------------------------
def extract_features(prompt, response, vectorizer):
    text = prompt + " " + response

    X_text = vectorizer.transform([text]).toarray()

    # Similarity
    vec_pair = vectorizer.transform([prompt, response])
    sim = cosine_similarity(vec_pair[0], vec_pair[1])[0][0]

    # Length features
    length = len(response)
    word_count = len(response.split())

    # Overlap
    overlap = len(set(prompt.lower().split()) & set(response.lower().split()))

    features = np.hstack((
        X_text,
        [[sim, length, word_count, overlap]]
    ))

    return features


# ---------------------------
# PREDICT
# ---------------------------
def predict_score(prompt: str, response: str) -> float:
    global _model, _vectorizer

    if _model is None or _vectorizer is None:
        if not _load():
            raise RuntimeError("Model not trained. Run train.py")

    features = extract_features(prompt, response, _vectorizer)

    score = _model.predict(features)[0]

    return round(max(0.0, min(10.0, float(score))), 2)


# ---------------------------
# TRAIN MODEL
# ---------------------------
def train_model(csv_path: str):
    global _model, _vectorizer

    print("[INFO] Loading dataset...")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    text = df["prompt"].astype(str) + " " + df["response"].astype(str)
    y = df["score"].astype(float).values

    print("[INFO] Building TF-IDF features...")
    vectorizer = TfidfVectorizer(max_features=5000)
    X_text = vectorizer.fit_transform(text)

    print("[INFO] Computing engineered features...")

    # Similarity
    vec_pair = vectorizer.transform(
        df["prompt"].astype(str).tolist() +
        df["response"].astype(str).tolist()
    )

    similarity = []
    for p, r in zip(df["prompt"], df["response"]):
        pair = vectorizer.transform([p, r])
        similarity.append(cosine_similarity(pair[0], pair[1])[0][0])

    similarity = np.array(similarity)

    # Length
    length = df["response"].str.len().values

    # Word count
    word_count = df["response"].str.split().apply(len).values

    # Overlap
    overlap = np.array([
        len(set(p.lower().split()) & set(r.lower().split()))
        for p, r in zip(df["prompt"], df["response"])
    ])

    # Combine all features
    X = np.hstack((
        X_text.toarray(),
        similarity.reshape(-1, 1),
        length.reshape(-1, 1),
        word_count.reshape(-1, 1),
        overlap.reshape(-1, 1)
    ))

    print("[INFO] Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("[INFO] Training GradientBoosting model...")
    model = GradientBoostingRegressor()

    model.fit(X_train, y_train)

    print("[INFO] Evaluating...")
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"[RESULT] MAE: {mae:.4f}")
    print(f"[RESULT] R2: {r2:.4f}")

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    _model = model
    _vectorizer = vectorizer

    return {
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "samples_used": len(df),
    }