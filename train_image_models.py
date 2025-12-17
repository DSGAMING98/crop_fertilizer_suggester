from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression

import joblib

# Optional deps
try:
    import cv2
except Exception:
    cv2 = None

try:
    from skimage.feature import local_binary_pattern
except Exception:
    local_binary_pattern = None



# Feature extraction (same idea as src/image_inference.py)


def _to_rgb_array(img: Image.Image, size=(224, 224)) -> np.ndarray:
    img = img.convert("RGB").resize(size)
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr


def extract_features(img: Image.Image) -> np.ndarray:
    """
    Extract fast features:
    - HSV histogram (or RGB histogram if cv2 missing)
    - LBP texture histogram (if skimage available)
    """
    arr = _to_rgb_array(img, size=(224, 224))

    # Color features
    if cv2 is not None:
        bgr = (arr[:, :, ::-1] * 255).astype(np.uint8)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        h_hist, _ = np.histogram(h, bins=32, range=(0, 180), density=True)
        s_hist, _ = np.histogram(s, bins=32, range=(0, 255), density=True)
        v_hist, _ = np.histogram(v, bins=32, range=(0, 255), density=True)
        color_feat = np.concatenate([h_hist, s_hist, v_hist]).astype(np.float32)
    else:
        r = (arr[:, :, 0] * 255).astype(np.uint8)
        g = (arr[:, :, 1] * 255).astype(np.uint8)
        b = (arr[:, :, 2] * 255).astype(np.uint8)
        r_hist, _ = np.histogram(r, bins=32, range=(0, 255), density=True)
        g_hist, _ = np.histogram(g, bins=32, range=(0, 255), density=True)
        b_hist, _ = np.histogram(b, bins=32, range=(0, 255), density=True)
        color_feat = np.concatenate([r_hist, g_hist, b_hist]).astype(np.float32)

    # Texture features (LBP)
    if local_binary_pattern is not None:
        gray = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114)
        gray = (gray * 255).astype(np.uint8)
        P, R = 24, 3
        lbp = local_binary_pattern(gray, P=P, R=R, method="uniform")
        lbp_hist, _ = np.histogram(lbp, bins=26, range=(0, 26), density=True)
        tex_feat = lbp_hist.astype(np.float32)
        feat = np.concatenate([color_feat, tex_feat]).astype(np.float32)
    else:
        feat = color_feat

    # Normalize
    feat = feat / (np.linalg.norm(feat) + 1e-9)
    return feat


def load_dataset(root_dir: Path) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    root_dir structure:
      root_dir/
        ClassA/*.jpg
        ClassB/*.jpg
    Returns: X, y, class_names
    """
    if not root_dir.exists():
        raise FileNotFoundError(f"Dataset folder not found: {root_dir}")

    class_dirs = [d for d in root_dir.iterdir() if d.is_dir()]
    class_dirs.sort(key=lambda x: x.name.lower())

    X_list = []
    y_list = []
    class_names = [d.name for d in class_dirs]

    valid_ext = {".jpg", ".jpeg", ".png", ".webp"}

    for class_idx, class_dir in enumerate(class_dirs):
        images = []
        for p in class_dir.rglob("*"):
            if p.suffix.lower() in valid_ext:
                images.append(p)

        if not images:
            print(f"[WARN] No images found in: {class_dir}")
            continue

        for img_path in images:
            try:
                img = Image.open(img_path)
                feat = extract_features(img)
                X_list.append(feat)
                y_list.append(class_idx)
            except Exception as e:
                print(f"[SKIP] {img_path.name} -> {e}")

    if not X_list:
        raise ValueError(f"No training images were loaded from: {root_dir}")

    X = np.vstack(X_list)
    y = np.array(y_list, dtype=np.int64)
    return X, y, class_names


def train_and_save(X, y, class_names: List[str], out_path: Path, test_size=0.2, seed=42):
    """
    Trains a simple LogisticRegression classifier with predict_proba support.
    Saves model with classes_ aligned to class_names.
    """
    # If dataset tiny, avoid stratify crash
    stratify = y if len(np.unique(y)) >= 2 and min(np.bincount(y)) >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=stratify
    )

    model = LogisticRegression(
        max_iter=2000,
        n_jobs=None,
        multi_class="auto",
    )
    model.fit(X_train, y_train)

    # attach correct class labels
    model.classes_ = np.array(class_names)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("\n==============================")
    print(f"[OK] Saved model to: {out_path}")
    print(f"[OK] Accuracy: {acc:.3f}")
    print("==============================\n")
    print(classification_report(y_test, y_pred))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_path)


def main():
    parser = argparse.ArgumentParser(description="Train soil/crop image models for Photo Mode.")
    parser.add_argument("--data_dir", type=str, default="data/image_training", help="Base training data directory.")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    base = project_root / args.data_dir

    soil_dir = base / "soil"
    crop_dir = base / "crop"

    models_dir = project_root / "models"
    soil_out = models_dir / "soil_img_model.joblib"
    crop_out = models_dir / "crop_img_model.joblib"

    print("=== Train Image Models ===")
    print(f"[INFO] Base data dir: {base}")
    print(f"[INFO] Soil dir: {soil_dir}")
    print(f"[INFO] Crop dir: {crop_dir}")
    print(f"[INFO] Models dir: {models_dir}\n")

    # Soil model
    print("----- Training SOIL model -----")
    X_soil, y_soil, soil_classes = load_dataset(soil_dir)
    train_and_save(X_soil, y_soil, soil_classes, soil_out, test_size=args.test_size, seed=args.seed)

    # Crop model
    print("\n----- Training CROP model -----")
    X_crop, y_crop, crop_classes = load_dataset(crop_dir)
    train_and_save(X_crop, y_crop, crop_classes, crop_out, test_size=args.test_size, seed=args.seed)

    print("\n✅ Done. Models created in /models/")
    print("Now Photo Mode will auto-detect soil/crop when you upload a photo.")


if __name__ == "__main__":
    main()
