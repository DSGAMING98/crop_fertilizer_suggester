import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import streamlit as st
from PIL import Image


# PATH SETUP — so `src` imports work even from /app/pages


PAGE_DIR = Path(__file__).resolve().parent              # .../app/pages
APP_DIR = PAGE_DIR.parent                               # .../app
PROJECT_ROOT = APP_DIR.parent                           # project root
SRC_DIR = PROJECT_ROOT / "src"

for p in (PROJECT_ROOT, SRC_DIR):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# Optional: If you want to ALSO run your full engine later
# from src.recommendation_engine import build_final_recommendation



# CSS


def inject_custom_css():
    css_path = APP_DIR / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)



# IMAGE HEURISTICS (NO MODEL NEEDED)


def _to_rgb(img: Image.Image, size=(256, 256)) -> np.ndarray:
    img = img.convert("RGB").resize(size)
    return np.asarray(img).astype(np.float32) / 255.0


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.max(rgb, axis=-1)
    cmin = np.min(rgb, axis=-1)
    diff = cmax - cmin

    h = np.zeros_like(cmax)
    mask = diff != 0

    idx = (cmax == r) & mask
    h[idx] = ((g[idx] - b[idx]) / diff[idx]) % 6
    idx = (cmax == g) & mask
    h[idx] = ((b[idx] - r[idx]) / diff[idx]) + 2
    idx = (cmax == b) & mask
    h[idx] = ((r[idx] - g[idx]) / diff[idx]) + 4
    h = (h / 6.0) % 1.0

    s = np.zeros_like(cmax)
    nonzero = cmax != 0
    s[nonzero] = diff[nonzero] / cmax[nonzero]

    v = cmax
    return np.stack([h, s, v], axis=-1)


def detect_soil_vs_plant(img: Image.Image) -> Tuple[str, float]:
    """
    Detect if image is mostly Plant vs Soil using green pixel fraction.
    """
    rgb = _to_rgb(img, (256, 256))
    hsv = _rgb_to_hsv(rgb)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    green = (h >= 0.20) & (h <= 0.45) & (s >= 0.22) & (v >= 0.18)
    green_frac = float(np.mean(green))

    # Tune threshold: lower = more likely to call plant
    if green_frac >= 0.08:
        conf = float(min(0.95, green_frac / 0.25))
        return "Plant", conf
    conf = float(min(0.95, (0.08 - green_frac) / 0.08))
    conf = max(0.55, conf)
    return "Soil", conf


def detect_soil_type(img: Image.Image) -> Tuple[str, float]:
    """
    Simple soil-type guess from brightness + saturation + texture variance.
    Works best on close-up soil photos.
    """
    rgb = _to_rgb(img, (256, 256))
    hsv = _rgb_to_hsv(rgb)
    v_mean = float(np.mean(hsv[..., 2]))
    s_mean = float(np.mean(hsv[..., 1]))

    gray = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
    texture = float(np.var(gray))  # higher = more grainy

    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]
    red_ratio = float(np.mean(r / (g + b + 1e-6)))

    # Very bright + low saturation => sand
    if v_mean > 0.62 and s_mean < 0.35:
        return "Sandy", 0.72

    # Very dark => loam or clay-ish
    if v_mean < 0.35:
        if red_ratio > 1.05:
            return "Clay", 0.62
        return "Loam", 0.70

    # Mid brightness => sandy loam vs silty clay based on texture
    if texture > 0.020:
        return "Sandy loam", 0.60
    return "Silty clay", 0.58


def detect_plant_type(img: Image.Image) -> Tuple[str, float]:
    """
    Broad plant type (NOT exact crop):
    - Grass-like (cereal-ish) vs Broadleaf
    """
    rgb = _to_rgb(img, (256, 256))
    gray = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114

    # Sobel-ish gradient (no extra deps)
    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    edge_strength = float(gx + gy)

    # If lots of fine edges + green => often grass-like (thin leaves)
    hsv = _rgb_to_hsv(rgb)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    green = (h >= 0.20) & (h <= 0.45) & (s >= 0.22) & (v >= 0.18)
    green_frac = float(np.mean(green))

    if green_frac >= 0.10 and edge_strength >= 0.08:
        return "Grass-like plant (possible cereal crop)", 0.62
    if green_frac >= 0.10:
        return "Broadleaf plant (possible vegetable/legume)", 0.58
    return "Plant detected (type unclear)", 0.50



# PHOTO-ONLY FERTILIZER RECOMMENDATION (AUTO)


def fertilizer_reco_auto(scene: str, soil_type: str | None, plant_type: str | None) -> Dict:
    """
    AUTO recommendation using ONLY what the photo tells us.
    No lab numbers. No crop dropdown.

    Output: a sensible plan + cautions.
    """
    soil = (soil_type or "Unknown").lower()
    plant = (plant_type or "Unknown").lower()

    # Base recommendation
    if scene == "Soil":
        main = "Balanced starter NPK + organic matter"
        plan = [
            "Add FYM/compost to improve structure + nutrient holding.",
            "Use a balanced starter fertilizer for general use: DAP/SSP (P) + MOP (K) + small split urea (N).",
            "If you later know the crop, dosing and timing can be refined."
        ]
        reasons = [
            "Photo alone can’t give NPK values, so a balanced approach is safer than single-urea.",
            "Organic matter supports long-term soil health across crops."
        ]
        cautions = [
            "For exact fertilizer amounts, soil test (NPK + pH) is needed."
        ]

    else:  # Plant photo
        if "grass-like" in plant:
            main = "Cereal-style plan: split urea + DAP/SSP + MOP"
            plan = [
                "Apply phosphorus at start (DAP/SSP) for rooting.",
                "Apply nitrogen as urea in split doses (not one heavy dose).",
                "Add MOP (potash) especially if soil is sandy/light or crop faces heat stress."
            ]
            reasons = [
                "Grass-like crops (cereals) are typically high nitrogen demand.",
                "Split N reduces losses and improves yield response."
            ]
            cautions = [
                "Don’t over-apply urea—too much N can cause weak stems and disease susceptibility."
            ]
        else:
            main = "Balanced plant plan: DAP/SSP + moderate N + potash as needed"
            plan = [
                "Use DAP/SSP as base for strong roots and flowering support.",
                "Use nitrogen (urea) in moderate splits depending on growth response.",
                "Use MOP if growth looks weak under stress or soil is light-textured."
            ]
            reasons = [
                "Broadleaf crops often need balanced N+P+K rather than heavy N-only feeding."
            ]
            cautions = [
                "Excess urea can push leafy growth and reduce fruiting/flowering for some crops."
            ]

    # Soil modifiers
    if "sandy" in soil:
        plan.append("Soil note: Sandy soil leaches nutrients → use smaller, frequent split applications + more compost.")
        cautions.append("Avoid heavy single urea dose on sandy soils (high loss by leaching).")
    elif "clay" in soil:
        plan.append("Soil note: Clay can waterlog → ensure drainage; prefer split N applications.")
        cautions.append("In wet clay, nitrogen losses can be high (denitrification).")
    elif "loam" in soil:
        plan.append("Soil note: Loam is balanced → standard split schedule works well.")
    elif "silty" in soil:
        plan.append("Soil note: Silty clay can compact → avoid over-watering; split fertilizer applications help.")

    return {
        "main": main,
        "plan": plan,
        "reasons": reasons,
        "cautions": cautions
    }



# UI


def pill(text: str, color="#22c55e"):
    return f"""
    <span style="
        display:inline-block;
        padding:0.18rem 0.60rem;
        border-radius:999px;
        background:{color};
        color:#0b1120;
        font-weight:900;
        font-size:0.80rem;
    ">{text}</span>
    """


def main():
    st.set_page_config(page_title="Photo Mode", page_icon="📸", layout="wide")
    inject_custom_css()

    st.title("📸 Photo Mode (Auto): Soil/Plant → Soil Type/Plant Type → Fertilizer")
    st.caption("No dropdowns. Upload a photo and it automatically tells what it is + recommends fertilizer based on the photo.")

    st.markdown("---")
    col_left, col_right = st.columns([1.1, 1.9], gap="large")

    with col_left:
        st.markdown("### 📷 Upload or take a photo")
        uploaded = st.file_uploader("Upload (soil or plant)", type=["png", "jpg", "jpeg", "webp"])
        cam = st.camera_input("Or take a photo")

        img_file = cam if cam is not None else uploaded
        if img_file is None:
            st.info("Upload/take a photo and results will show automatically.")
            return

        img = Image.open(img_file)
        st.image(img, use_container_width=True)

    with col_right:
        # AUTO RUN on upload
        with st.spinner("Auto-analyzing photo…"):
            scene, scene_conf = detect_soil_vs_plant(img)

            soil_type = None
            soil_conf = 0.0
            plant_type = None
            plant_conf = 0.0

            if scene == "Soil":
                soil_type, soil_conf = detect_soil_type(img)
            else:
                plant_type, plant_conf = detect_plant_type(img)

        st.markdown("## 🧠 What the photo is")
        if scene == "Soil":
            st.markdown(f"{pill('SOIL PHOTO', '#22c55e')}  confidence: **{scene_conf:.0%}**", unsafe_allow_html=True)
        else:
            st.markdown(f"{pill('PLANT PHOTO', '#22c55e')}  confidence: **{scene_conf:.0%}**", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("## 🔎 Auto detection results")

        c1, c2 = st.columns(2, gap="large")

        with c1:
            st.markdown("### 🌱 Soil type")
            if scene == "Soil":
                st.success(f"{soil_type}  (confidence ~ {soil_conf:.0%})")
            else:
                st.info("Not applicable (plant photo)")

        with c2:
            st.markdown("### 🌿 Plant / Crop")
            if scene == "Plant":
                # We are not doing exact crop without a trained model
                st.success(f"{plant_type}  (confidence ~ {plant_conf:.0%})")
                st.caption("Exact crop name requires a trained crop image model (optional upgrade).")
            else:
                st.info("Not applicable (soil photo)")

        st.markdown("---")
        st.markdown("## 🌿 Fertilizer Recommendation (AUTO from photo)")

        reco = fertilizer_reco_auto(scene, soil_type, plant_type)

        st.success(f"✅ Recommended: {reco['main']}")

        st.markdown("### Plan")
        for step in reco["plan"]:
            st.write(f"- {step}")

        st.markdown("### Why this")
        for r in reco["reasons"]:
            st.write(f"- {r}")

        if reco["cautions"]:
            st.markdown("### Cautions")
            for c in reco["cautions"]:
                st.warning(c)

        st.markdown("---")
        st.caption("This is a photo-only recommendation. For precise fertilizer amounts/doses, use soil test values (NPK+pH).")


if __name__ == "__main__":
    main()
