import sys
from pathlib import Path


# PATH SETUP — MAKE SURE `src` IMPORTS WORK


APP_DIR = Path(__file__).resolve().parent          # .../crop_fertilizer_suggester/app
PROJECT_ROOT = APP_DIR.parent                      # .../crop_fertilizer_suggester
SRC_DIR = PROJECT_ROOT / "src"

for p in (PROJECT_ROOT, SRC_DIR):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

import streamlit as st

from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_DESCRIPTION,
    SUPPORTED_CROPS,
    ensure_directories_exist,
)
from src.recommendation_engine import build_final_recommendation



# STREAMLIT PAGE CONFIG


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🌾",
    layout="wide",
)



# CUSTOM CSS


def inject_custom_css():
    # you have app/assets/styles.css
    css_path = APP_DIR / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# HEADER


def render_header():
    st.title(f"🌾 {APP_TITLE}")
    st.subheader(APP_SUBTITLE)
    st.markdown(
        f"""
        <div style="font-size: 0.95rem; color: #ccc;">
            {APP_DESCRIPTION}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")



# INPUT FORM


def get_user_input() -> dict:
    st.markdown("### 🧪 Enter soil test values & crop")

    with st.form("soil_input_form"):
        col1, col2 = st.columns(2)

        with col1:
            pH = st.number_input("Soil pH", min_value=3.5, max_value=10.0, value=6.5, step=0.1)
            organic_carbon = st.number_input(
                "Organic Carbon (%)",
                min_value=0.0,
                max_value=5.0,
                value=0.8,
                step=0.05,
            )
            nitrogen = st.number_input(
                "Available Nitrogen (kg/ha)",
                min_value=0.0,
                max_value=500.0,
                value=80.0,
                step=5.0,
            )
            phosphorus = st.number_input(
                "Available Phosphorus (kg/ha)",
                min_value=0.0,
                max_value=200.0,
                value=25.0,
                step=1.0,
            )
            potassium = st.number_input(
                "Available Potassium (kg/ha)",
                min_value=0.0,
                max_value=600.0,
                value=150.0,
                step=5.0,
            )

        with col2:
            soil_type = st.selectbox(
                "Soil type",
                options=[
                    "Loam",
                    "Clay",
                    "Sandy",
                    "Sandy loam",
                    "Silty clay",
                ],
                index=0,
            )
            rainfall = st.number_input(
                "Seasonal rainfall (mm)",
                min_value=0.0,
                max_value=3000.0,
                value=800.0,
                step=10.0,
            )
            temperature = st.number_input(
                "Average temperature (°C)",
                min_value=5.0,
                max_value=50.0,
                value=28.0,
                step=0.5,
            )
            ec = st.number_input(
                "Electrical conductivity EC (dS/m)",
                min_value=0.0,
                max_value=10.0,
                value=0.6,
                step=0.05,
            )
            crop = st.selectbox(
                "Target crop",
                options=SUPPORTED_CROPS,
                index=0,
            )

        submitted = st.form_submit_button("🔍 Get fertilizer suggestion")

    if not submitted:
        return {}

    return {
        "pH": float(pH),
        "organic_carbon": float(organic_carbon),
        "nitrogen": float(nitrogen),
        "phosphorus": float(phosphorus),
        "potassium": float(potassium),
        "soil_type": soil_type,
        "rainfall": float(rainfall),
        "temperature": float(temperature),
        "ec": float(ec),
        "crop": crop,
    }



# RENDER HELPERS


def render_soil_health(soil_health: dict):
    st.markdown("### 🌍 Soil health overview")

    idx = soil_health.get("index", None)
    cat = soil_health.get("category", "Unknown")
    factors = soil_health.get("factor_scores", {})

    if idx is None:
        st.info("Soil health index could not be computed.")
        return

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Soil Health Index (0–1)", value=f"{idx:.2f}")
    with col2:
        st.success(f"Overall soil health category: {cat}")

    if factors:
        with st.expander("See factor-wise soil health explanation"):
            for key, info in factors.items():
                score = info.get("score", 0.0)
                level = info.get("level", "unknown")
                msg = info.get("message", "")
                st.markdown(f"**{key.upper()}** – score: `{score:.2f}` | level: `{level}`")
                st.write(msg)
                st.markdown("---")


def render_rule_based_output(rules_out: dict):
    st.markdown("### 📐 Rule-based fertilizer logic (agronomy + chemistry)")

    npk_status = rules_out.get("npk_status", {})
    ph_band = rules_out.get("ph_band", "unknown")
    recs = rules_out.get("primary_recommendations", [])
    warnings = rules_out.get("warnings", [])
    notes = rules_out.get("notes", [])

    st.markdown("**NPK status**")
    st.write(
        {
            "N": npk_status.get("N", "unknown"),
            "P": npk_status.get("P", "unknown"),
            "K": npk_status.get("K", "unknown"),
        }
    )
    st.write(f"**pH band:** `{ph_band}`")

    if recs:
        st.markdown("**Recommended fertilizers (rule-based):**")
        for r in recs:
            name = r["name"]
            priority = r.get("priority", 99)
            nutrients = r.get("nutrients", {})
            reasons = r.get("reasons", [])

            with st.expander(f"{priority}. {name}"):
                st.markdown("**Nutrient profile:**")
                st.write(nutrients)
                st.markdown("**Why this fertilizer?**")
                for reason in reasons:
                    st.markdown(f"- {reason}")
    else:
        st.info("No rule-based recommendations could be generated.")

    if warnings:
        st.markdown("**⚠️ Warnings:**")
        for w in warnings:
            st.warning(w)

    if notes:
        st.markdown("**📝 Notes:**")
        for n in notes:
            st.info(n)


def render_ml_output(ml_out: dict):
    st.markdown("### 🤖 ML model insight")

    if not ml_out.get("available", False):
        msg = ml_out.get("message", "ML model is not available yet.")
        st.info(msg)
        return

    pred = ml_out.get("predicted_fertilizer")
    probs = ml_out.get("probabilities")

    if pred is None:
        st.info("ML model did not return a clear fertilizer prediction.")
        return

    st.success(f"ML-predicted fertilizer: `{pred}`")

    if probs:
        st.markdown("**Class probabilities:**")
        sorted_items = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        for label, p in sorted_items:
            st.write(f"- `{label}` → {p:.2%}")


def render_final_choice(final_choice: dict):
    st.markdown("### ✅ Final recommendation")

    name = final_choice.get("name")
    source = final_choice.get("source", "none")
    rationale = final_choice.get("rationale", "")

    if name is None:
        st.error(
            "No clear fertilizer recommendation could be produced. "
            "Please re-check soil data or consult a local agronomist."
        )
        return

    source_label = {
        "ml+rules": "ML + Rule-based (both agree)",
        "ml_only": "ML-only (data-driven)",
        "rules_only": "Rule-based agronomy",
        "none": "Unknown source",
    }.get(source, source)

    st.success(f"Recommended fertilizer: `{name}`")
    st.caption(f"Source of decision: {source_label}")
    st.markdown("**Why this recommendation?**")
    st.write(rationale)


def render_chemistry_learn_section():
    st.markdown("### 🧬 Chemistry behind fertilizers (quick learning corner)")
    st.write(
        """
This tool is not just giving an answer – it links fertilizer choice to the underlying chemistry:

- Nitrogenous fertilizers (e.g., Urea, Ammonium sulphate): Supply N mainly as ammonium or urea, which hydrolyses to ammonium and then nitrifies to nitrate. They strongly influence leaf growth and canopy development.
- Phosphatic fertilizers (DAP, SSP): Provide phosphorus as orthophosphate ions. P is key for roots, energy transfer (ATP/ADP) and early crop establishment.
- Potassic fertilizers (MOP): Supply K⁺ ions, which regulate stomatal opening, osmotic balance and stress tolerance.
- Organic manures (FYM, Vermicompost): Slowly release a mix of nutrients, increase cation exchange capacity, and buffer pH changes.
- Biofertilizers: Use living microbes to fix nitrogen, solubilise phosphate or mobilise nutrients already present in soil.
        """
    )
    st.info(
        "As you change the soil test values on the left, observe how the "
        "recommended fertilizers and explanations shift – that’s your "
        "experiential learning piece."
    )


def render_project_credits():
    st.markdown("---")
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 0.85rem;
            color: #aaaaaa;
            padding: 1.2rem 0.4rem;
        ">
            <b>Crop–Fertilizer Suggestion System</b> 🌾<br>
            <span style="font-size: 0.8rem;">
                Experiential Learning Project – Smart Agriculture & Chemistry of Fertilizers
            </span>
            <br><br>
            <b>Project Credits</b><br>
            👨‍💻 Monish Kandanuru (Coder)<br>
            👨‍💻 Shanmukha Sai (Coder)<br>
            🧠 Parameshwar Sahoo<br>
            🧠 Nandan Gowda<br>
            🧠 Mohumad Hashim
            <br><br>
            <span style="font-size: 0.7rem; color: #888888;">
                © 2025 | All rights reserved
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )



# MAIN


def main():
    ensure_directories_exist()
    inject_custom_css()
    render_header()

    col_left, col_right = st.columns([1.1, 1.9])

    with col_left:
        input_data = get_user_input()

    with col_right:
        if not input_data:
            st.info("Fill the soil and crop details on the left, then click the button.")
        else:
            result = build_final_recommendation(input_data)

            soil_health = result.get("soil_health", {})
            rules_out = result.get("rules", {})
            ml_out = result.get("ml", {})
            final_choice = result.get("final_choice", {})

            render_final_choice(final_choice)
            st.markdown("---")
            render_soil_health(soil_health)
            st.markdown("---")
            render_rule_based_output(rules_out)
            st.markdown("---")
            render_ml_output(ml_out)
            st.markdown("---")
            render_chemistry_learn_section()

    # footer always at the very bottom
    render_project_credits()


if __name__ == "__main__":
    main()
