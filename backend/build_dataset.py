import os
import pandas as pd
import random
import numpy as np
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# CONFIG
# ---------------------------
data = []
all_texts = []

TARGET_SIZE = 50000

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "real_dataset_50k.csv")

# ---------------------------
# LOAD DATA FIRST (NO SCORING)
# ---------------------------

print("[1/4] Loading Alpaca...")
alpaca = load_dataset("tatsu-lab/alpaca", split="train")

for row in alpaca:
    prompt = str(row["instruction"]).strip()
    response = str(row["output"]).strip()

    if prompt and response and len(response) > 5:
        data.append([prompt, response])
        all_texts.append(prompt)
        all_texts.append(response)

print("   Alpaca done")

# ---------------------------
print("[2/4] Loading Dolly...")
dolly = load_dataset("databricks/databricks-dolly-15k", split="train")

for row in dolly:
    prompt = str(row["instruction"]).strip()
    response = str(row["response"]).strip()

    if prompt and response and len(response) > 5:
        data.append([prompt, response])
        all_texts.append(prompt)
        all_texts.append(response)

print("   Dolly done")

# ---------------------------
print("[3/4] Loading OpenAssistant...")
oasst = load_dataset("OpenAssistant/oasst1", split="train")

for row in oasst:
    if row["role"] == "assistant":
        response = str(row["text"]).strip()
        prompt = "Explain the concept."

        if response and len(response) > 5:
            data.append([prompt, response])
            all_texts.append(prompt)
            all_texts.append(response)

print("   OASST done")

# ---------------------------
print("[4/4] Loading HH-RLHF...")
hh = load_dataset("Anthropic/hh-rlhf", split="train")

for row in hh:
    try:
        prompt = row["chosen"].split("\n\nAssistant:")[0].replace("Human:", "").strip()

        good_resp = row["chosen"].split("Assistant:")[-1].strip()
        bad_resp = row["rejected"].split("Assistant:")[-1].strip()

        if prompt and good_resp:
            data.append([prompt, good_resp])
            all_texts.append(prompt)
            all_texts.append(good_resp)

        if prompt and bad_resp:
            data.append([prompt, bad_resp])
            all_texts.append(prompt)
            all_texts.append(bad_resp)

    except:
        continue

print("   HH-RLHF done")

# ---------------------------
# FIT TF-IDF ONCE (IMPORTANT)
# ---------------------------
print("\n[INFO] Fitting TF-IDF vectorizer...")

vectorizer = TfidfVectorizer(max_features=3000)
vectorizer.fit(all_texts)

# ---------------------------
# SCORING FUNCTION
# ---------------------------
def compute_score(prompt, response):
    try:
        vec = vectorizer.transform([prompt, response])
        sim = cosine_similarity(vec[0], vec[1])[0][0]
    except:
        sim = 0

    length = len(response)
    overlap = len(set(prompt.lower().split()) & set(response.lower().split()))

    score = (
        sim * 5.0 +                # semantic similarity
        min(length / 100, 3) +    # length score
        min(overlap, 2)           # keyword overlap
    )

    return round(min(score, 10), 2)

# ---------------------------
# APPLY SCORING
# ---------------------------
print("[INFO] Computing scores...")

final_data = []

for prompt, response in data:
    score = compute_score(prompt, response)

    # RLHF-like adjustment
    if score > 7:
        score += 1
    elif score < 3:
        score -= 1

    score = max(0, min(score, 10))

    final_data.append([prompt, response, score])

# ---------------------------
# FINAL PROCESSING
# ---------------------------
print(f"\n[INFO] Total rows before shuffle: {len(final_data)}")

random.shuffle(final_data)
final_data = final_data[:TARGET_SIZE]

os.makedirs(DATA_DIR, exist_ok=True)

df = pd.DataFrame(final_data, columns=["prompt", "response", "score"])
df.to_csv(OUTPUT_PATH, index=False)

print(f"[SUCCESS] Dataset saved → {OUTPUT_PATH}")
print(f"[INFO] Final size: {len(df)}")