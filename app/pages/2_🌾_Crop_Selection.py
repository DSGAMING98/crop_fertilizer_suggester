import sys
from pathlib import Path

# Make sure Python can see the project root (where `src` lives)
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.config import (
    APP_TITLE,
    SUPPORTED_CROPS,
    ensure_directories_exist,
)
from src.recommendation_engine import build_final_recommendation



st.set_page_config(
    page_title=f"{APP_TITLE} – Crop Selection",
    page_icon="🌱",
    layout="wide",
)


def render_header():
    st.title("🌱 Crop Selection & Fertilizer Comparison")
    st.caption(
        "Fix one soil condition and compare how different crops change the fertilizer recommendation."
    )
    st.markdown("---")


def get_base_soil_input() -> dict:
    st.markdown("### 🧪 Base soil condition (same for all crops)")

    with st.form("crop_selection_soil_form"):
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

        compare_crops = st.multiselect(
            "Select crops to compare",
            options=SUPPORTED_CROPS,
            default=min(3, len(SUPPORTED_CROPS)) and SUPPORTED_CROPS[:3],
            help="These crops will be compared under the same soil condition.",
        )

        submitted = st.form_submit_button("🔍 Compare fertilizers for selected crops")

    if not submitted:
        return {}, []

    base_soil = {
        "pH": float(pH),
        "organic_carbon": float(organic_carbon),
        "nitrogen": float(nitrogen),
        "phosphorus": float(phosphorus),
        "potassium": float(potassium),
        "soil_type": soil_type,
        "rainfall": float(rainfall),
        "temperature": float(temperature),
        "ec": float(ec),
    }

    return base_soil, compare_crops


def render_comparison(base_soil: dict, crops: list[str]):
    if not crops:
        st.info("Select at least one crop to compare.")
        return

    st.markdown("### 📊 Fertilizer recommendation by crop")
    st.caption("Same soil → different crops → different fertilizer strategy.")

    cols = st.columns(len(crops))

    for i, crop in enumerate(crops):
        with cols[i]:
            input_data = dict(base_soil)
            input_data["crop"] = crop

            result = build_final_recommendation(input_data)
            final_choice = result.get("final_choice", {})
            rules_out = result.get("rules", {})
            soil_health = result.get("soil_health", {})

            fert_name = final_choice.get("name")
            source = final_choice.get("source", "none")
            rationale = final_choice.get("rationale", "")

            source_label = {
                "ml+rules": "ML + Rules",
                "ml_only": "ML only",
                "rules_only": "Rules only",
                "none": "Unknown",
            }.get(source, source)

            st.markdown(f"#### 🌾 {crop}")

            # Soil health mini view
            sh_idx = soil_health.get("index", None)
            sh_cat = soil_health.get("category", None)

            if sh_idx is not None and sh_cat is not None:
                st.metric("Soil Health Index", f"{sh_idx:.2f}", help=f"Category: {sh_cat}")
            else:
                st.caption("Soil health index not available.")

            if fert_name is None:
                st.error("No clear fertilizer recommendation.")
            else:
                st.success(f"`{fert_name}`")
                st.caption(f"Decision source: {source_label}")

            # Tiny NPK + pH summary
            npk_status = rules_out.get("npk_status", {})
            ph_band = rules_out.get("ph_band", "unknown")

            st.markdown("**NPK status:**")
            st.write(
                {
                    "N": npk_status.get("N", "unknown"),
                    "P": npk_status.get("P", "unknown"),
                    "K": npk_status.get("K", "unknown"),
                }
            )
            st.write(f"**pH band:** `{ph_band}`")

            with st.expander("Why this fertilizer?"):
                if rationale:
                    st.write(rationale)
                else:
                    st.write("No detailed rationale available.")


def main():
    ensure_directories_exist()
    render_header()

    col_left, col_right = st.columns([1.1, 1.9])

    with col_left:
        base_soil, crops = get_base_soil_input()

    with col_right:
        if not base_soil:
            st.info("Set your base soil condition and choose crops on the left.")
        else:
            render_comparison(base_soil, crops)
            st.markdown("---")
            st.info(
                "Use this page to show that fertilizer recommendations are not just about soil, "
                "but also about the crop’s nutrient demand and agronomy."
            )


if __name__ == "__main__":
    main()
