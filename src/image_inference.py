from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

try:
    import joblib
except Exception:
    joblib = None


@dataclass
class ImagePrediction:
    label: Optional[str]
    confidence: float
    available: bool
    message: str = ""



# Utility


def _to_rgb_array(img: Image.Image, size: Tuple[int, int] = (256, 256)) -> np.ndarray:
    img = img.convert("RGB").resize(size)
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """
    Vectorized RGB->HSV for rgb in [0,1]. Output HSV in [0,1].
    rgb: (H,W,3)
    """
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]

    cmax = np.max(rgb, axis=-1)
    cmin = np.min(rgb, axis=-1)
    diff = cmax - cmin

    # Hue
    h = np.zeros_like(cmax)
    mask = diff != 0

    # where cmax == r
    idx = (cmax == r) & mask
    h[idx] = ((g[idx] - b[idx]) / diff[idx]) % 6

    # where cmax == g
    idx = (cmax == g) & mask
    h[idx] = ((b[idx] - r[idx]) / diff[idx]) + 2

    # where cmax == b
    idx = (cmax == b) & mask
    h[idx] = ((r[idx] - g[idx]) / diff[idx]) + 4

    h = (h / 6.0) % 1.0

    # Saturation
    s = np.zeros_like(cmax)
    nonzero = cmax != 0
    s[nonzero] = diff[nonzero] / cmax[nonzero]

    # Value
    v = cmax

    return np.stack([h, s, v], axis=-1)



# 1) Scene detection: soil vs plant


def detect_scene(img: Image.Image) -> ImagePrediction:
    """
    Heuristic:
    - If there's enough green foliage pixels -> Plant
    - Else -> Soil
    """
    rgb = _to_rgb_array(img, (256, 256))
    hsv = _rgb_to_hsv(rgb)

    h = hsv[..., 0]  # 0..1
    s = hsv[..., 1]
    v = hsv[..., 2]

    # green-ish mask: hue ~ [0.20, 0.45] and decent saturation/value
    green = (h >= 0.20) & (h <= 0.45) & (s >= 0.20) & (v >= 0.20)
    green_frac = float(np.mean(green))

    if green_frac >= 0.08:
        conf = min(0.95, green_frac / 0.25)  # scale
        return ImagePrediction(label="Plant", confidence=conf, available=True, message="heuristic")
    else:
        conf = min(0.95, (0.08 - green_frac) / 0.08)
        conf = max(0.55, conf)  # don’t go too low
        return ImagePrediction(label="Soil", confidence=conf, available=True, message="heuristic")



# 2) Soil type (heuristic)


def soil_type_heuristic(img: Image.Image) -> ImagePrediction:
    """
    VERY approximate visual heuristic for soil:
    - Sandy: lighter + more yellow + lower saturation
    - Loam: dark brown + moderate texture
    - Clay: reddish/brown + smoother
    - Sandy loam: mid brightness + higher texture
    - Silty clay: mid-dark + smoother/less texture
    """
    rgb = _to_rgb_array(img, (256, 256))
    hsv = _rgb_to_hsv(rgb)

    v_mean = float(np.mean(hsv[..., 2]))
    s_mean = float(np.mean(hsv[..., 1]))

    # texture proxy: grayscale variance
    gray = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    texture = float(np.var(gray))

    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]
    red_ratio = float(np.mean(r / (g + b + 1e-6)))

    # Rules
    if v_mean > 0.62 and s_mean < 0.35:
        return ImagePrediction(label="Sandy", confidence=0.70, available=True, message="heuristic")
    if v_mean < 0.35:
        # very dark -> loam/clay
        if red_ratio > 1.05:
            return ImagePrediction(label="Clay", confidence=0.65, available=True, message="heuristic")
        return ImagePrediction(label="Loam", confidence=0.70, available=True, message="heuristic")

    # mid brightness
    if texture > 0.020:
        return ImagePrediction(label="Sandy loam", confidence=0.60, available=True, message="heuristic")
    else:
        return ImagePrediction(label="Silty clay", confidence=0.58, available=True, message="heuristic")



# 3) Crop model inference (optional)


def _load_model(model_path: Path):
    if joblib is None:
        return None, "joblib not installed"
    if not model_path.exists():
        return None, "model file not found"
    try:
        model = joblib.load(model_path)
        return model, ""
    except Exception as e:
        return None, f"failed to load model: {e}"


def _extract_simple_features(img: Image.Image) -> np.ndarray:
    """
    Small feature vector used for any sklearn model you might train later.
    """
    rgb = _to_rgb_array(img, (224, 224))
    hsv = _rgb_to_hsv(rgb)

    # histograms (fast)
    h = hsv[..., 0]
    s = hsv[..., 1]
    v = hsv[..., 2]

    h_hist, _ = np.histogram(h, bins=24, range=(0, 1), density=True)
    s_hist, _ = np.histogram(s, bins=24, range=(0, 1), density=True)
    v_hist, _ = np.histogram(v, bins=24, range=(0, 1), density=True)

    # texture proxy
    gray = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    t_var = np.array([np.var(gray)], dtype=np.float32)

    feat = np.concatenate([h_hist, s_hist, v_hist, t_var]).astype(np.float32)
    feat = feat / (np.linalg.norm(feat) + 1e-9)
    return feat.reshape(1, -1)


def predict_crop_from_model(img: Image.Image, model_path: Path, min_conf: float = 0.55) -> ImagePrediction:
    model, err = _load_model(model_path)
    if model is None:
        return ImagePrediction(label=None, confidence=0.0, available=False, message=err)

    feat = _extract_simple_features(img)

    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(feat)[0]
        classes = list(getattr(model, "classes_", []))
        if not classes:
            return ImagePrediction(label=None, confidence=0.0, available=False, message="model has no classes_")

        best_idx = int(np.argmax(probs))
        label = str(classes[best_idx])
        conf = float(probs[best_idx])

        if conf < min_conf:
            return ImagePrediction(label=None, confidence=conf, available=True, message="low confidence")
        return ImagePrediction(label=label, confidence=conf, available=True, message="model")
    else:
        pred = model.predict(feat)[0]
        return ImagePrediction(label=str(pred), confidence=0.60, available=True, message="model (no proba)")



# Main API used by the app page


def predict_scene_soil_crop(img: Image.Image, project_root: Path) -> Tuple[ImagePrediction, ImagePrediction, ImagePrediction]:
    """
    Returns: scene_pred, soil_pred, crop_pred
    - If scene is Soil => soil_pred is heuristic/model; crop_pred usually None
    - If scene is Plant => crop_pred model if exists; soil_pred heuristic if needed
    """
    scene = detect_scene(img)

    models_dir = project_root / "models"
    crop_model_path = models_dir / "crop_img_model.joblib"  # optional

    if scene.label == "Soil":
        soil_pred = soil_type_heuristic(img)
        crop_pred = ImagePrediction(label=None, confidence=0.0, available=False, message="not a plant photo")
        return scene, soil_pred, crop_pred

    # Plant photo
    crop_pred = predict_crop_from_model(img, crop_model_path)
    soil_pred = ImagePrediction(label=None, confidence=0.0, available=False, message="plant photo (soil not visible)")
    return scene, soil_pred, crop_pred
