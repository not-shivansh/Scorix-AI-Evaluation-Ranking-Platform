# 🚀 Scorix AI — AI Evaluation & Ranking Platform

> **Production-grade AI evaluation system** that scores, ranks, and improves AI-generated responses using machine learning and real-time APIs.

---

## 🌟 Overview

**Scorix AI** is a full-stack AI benchmarking platform that simulates **enterprise-level LLM evaluation systems**.

It allows you to:

* ⚡ Evaluate AI responses using ML models
* 🧠 Rank multiple responses intelligently
* 📊 Track evaluation logs & feedback
* 🔁 Retrain models with new datasets

---

## 🎯 Key Features

### 🧪 AI Evaluation Engine

* Scores responses using:

  * TF-IDF vectorization
  * Cosine similarity
  * Feature engineering
* Output: **0–10 quality score**

---

### 🏆 Ranking System

* Compare multiple responses for a prompt
* Returns ranked list based on score

---

### 📊 Feedback Learning (RLHF-style)

* Store human feedback
* Use for retraining and improvement

---

### 🔁 Dataset Upload + Retraining

* Upload CSV dataset
* Retrain model via API

---

## 🧠 ML Model

### ⚙️ Architecture

```text
TF-IDF (5000 features)
+ Cosine Similarity
+ Length Features
+ Word Count
+ Keyword Overlap
→ Gradient Boosting Regressor
```

---

## 📈 Model Performance

* 🔥 **R² Score:** 0.9658
* 🔥 **MAE:** 0.2558
* 📊 Dataset Size: 50,000 samples

---

## 🧠 Architecture

```text
Frontend (Vanilla JS)
        ↓
FastAPI Backend
        ↓
ML Model (TF-IDF + Gradient Boosting)
        ↓
Evaluation + Ranking Engine
        ↓
Database (SQLite)
```

---

## 🛠️ Tech Stack

| Layer    | Technology                 |
| -------- | -------------------------- |
| Backend  | FastAPI                    |
| ML Model | Scikit-learn               |
| NLP      | TF-IDF + Cosine Similarity |
| Database | SQLite                     |
| ORM      | SQLAlchemy                 |
| Frontend | HTML, CSS, Vanilla JS      |
| Server   | Uvicorn                    |

---

## ⚡ Quick Start

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Run server

```bash
python -m uvicorn backend.main:app --reload
```

---

### 🌐 Open

* App → http://localhost:8000
* Docs → http://localhost:8000/docs

---

## 📡 API Endpoints

### 🔹 Evaluate Response

```http
POST /evaluate
```

```json
{
  "prompt": "What is AI?",
  "response": "AI is the simulation of human intelligence in machines."
}
```

---

### 🔹 Rank Responses

```http
POST /rank
```

```json
{
  "prompt": "What is AI?",
  "responses": [
    "AI is computer intelligence.",
    "AI is the simulation of human intelligence in machines.",
    "AI is random."
  ]
}
```

---

### 🔹 Submit Feedback

```http
POST /feedback
```

---

### 🔹 Upload Dataset + Retrain

```http
POST /upload-dataset
```

---

### 🔹 Health Check

```http
GET /health
```

---

## 📸 Screenshots

```markdown

```

---

## 🧠 What Makes This Special

✔ End-to-end ML pipeline (dataset → training → deployment)
✔ Real-time scoring & ranking APIs
✔ Feature-engineered ML model (not just black-box)
✔ RLHF-style feedback system

---

## 🚀 Future Improvements

* 🔁 Reinforcement learning (RLHF loop)
* 📊 Model comparison leaderboard
* ⚡ Async batch evaluation
* 🧠 Deep learning-based scoring

---

## 👨‍💻 Author

**Shivansh Thakur** ([Linkedin](https://linkedin.com/in/thakur-shivansh))

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub 🚀
