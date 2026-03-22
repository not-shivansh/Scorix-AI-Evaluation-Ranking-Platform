"""
Scorix AI - Training Script (TF-IDF Version)
Trains the TF-IDF + Ridge regression model.

Usage:
    python train.py
"""

import os
import sys

# 👉 update import based on your structure
# If inside app/ml/
# from app.ml.model import train_model

# If same folder:
from model import train_model


# ---------------------------
# PATHS
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "real_dataset_50k.csv")


# ---------------------------
# MAIN
# ---------------------------
def main():
    print("=" * 50)
    print("  Scorix AI - TF-IDF Model Training")
    print("=" * 50)

    # Check dataset
    if not os.path.exists(DATASET_PATH):
        print(f"\n[ERROR] Dataset not found at: {DATASET_PATH}")
        print("👉 Run: python build_dataset.py first")
        sys.exit(1)

    print(f"\n[DATASET] {DATASET_PATH}")
    print("[INFO] Training model (TF-IDF + Ridge)...\n")

    try:
        metrics = train_model(DATASET_PATH)

        print("\n[SUCCESS] Training Complete!")
        print(f"   Samples Used : {metrics['samples_used']}")
        print(f"   MAE          : {metrics['mae']}")
        print(f"   R2 Score     : {metrics['r2']}")

        print("\n[SAVED] Model + Vectorizer saved in data/ directory.")

    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        sys.exit(1)


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    main()