"""
Train ML model for Crop-Fertilizer Suggestion System.

Steps:
1. Load processed training_dataset.csv
2. Split into train/test
3. Fit preprocessor (scaler + one-hot encoder)
4. Train classifier (RandomForest by default)
5. Evaluate on test set
6. Save preprocessor + model to /models
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

from src.config import (
    RANDOM_STATE,
    MODEL_FILE,
    SCALER_FILE,
    ensure_directories_exist,
)
from src.data_loader import load_training_dataset
from src.preprocess import (
    split_features_target,
    fit_preprocessor,
    transform_features,
    save_preprocessor,
)


def main():
    print("=== Crop-Fertilizer ML Training ===")

    # Make sure folders exist
    ensure_directories_exist()
    print("[OK] Directories checked/created.")

    # 1) Load training dataset
    try:
        df = load_training_dataset()
    except FileNotFoundError as e:
        print("\n[ERROR] Training dataset not found.")
        print(e)
        print(
            "\nCreate 'data/processed/training_dataset.csv' with columns like:\n"
            "  pH, organic_carbon, nitrogen, phosphorus, potassium,\n"
            "  soil_type, rainfall, temperature, ec, crop, recommended_fertilizer\n"
        )
        return

    print(f"[OK] Training dataset loaded. Shape = {df.shape}")

    # 2) Split features & target
    try:
        X, y = split_features_target(df)
    except ValueError as e:
        print("\n[ERROR] Problem with training dataframe columns:")
        print(e)
        return

    print(f"[INFO] Features shape: {X.shape}, Target length: {len(y)}")

    # 3) Train/test split
    # First try stratified split; if classes are too small, fall back to normal split.
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=RANDOM_STATE,
            stratify=y,
        )
        print("[OK] Stratified train/test split completed.")
    except ValueError as e:
        print("\n[WARN] Stratified split failed:")
        print(f"      {e}")
        print("      Falling back to non-stratified train/test split.\n")
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=RANDOM_STATE,
            stratify=None,
        )
        print("[OK] Non-stratified train/test split completed.")

    print(
        f"[INFO] Train size: {X_train.shape[0]} rows, "
        f"Test size: {X_test.shape[0]} rows"
    )

    # 4) Fit preprocessor on TRAIN only
    preprocessor = fit_preprocessor(X_train)
    print("[OK] Preprocessor (scaler + encoder) fitted.")

    # 5) Transform features
    X_train_trans = transform_features(preprocessor, X_train)
    X_test_trans = transform_features(preprocessor, X_test)

    print("[OK] Features transformed.")
    print(f"[DEBUG] X_train_trans shape: {X_train_trans.shape}")
    print(f"[DEBUG] X_test_trans shape: {X_test_trans.shape}")

    # 6) Train classifier
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("[INFO] Training RandomForestClassifier...")
    model.fit(X_train_trans, y_train)
    print("[OK] Model training complete.")

    # 7) Evaluate
    y_pred = model.predict(X_test_trans)
    acc = accuracy_score(y_test, y_pred)
    print("\n=== Evaluation on Test Set ===")
    print(f"Accuracy: {acc:.4f}\n")
    print("Classification report:")
    print(classification_report(y_test, y_pred))

    # 8) Save preprocessor + model
    save_preprocessor(preprocessor, path=SCALER_FILE)
    print(f"[OK] Preprocessor saved to: {SCALER_FILE}")

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    print(f"[OK] Model saved to: {MODEL_FILE}")

    print("\n=== Training pipeline finished successfully ===")


if __name__ == "__main__":
    main()
