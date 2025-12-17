import streamlit as st
# cd crop_fertilizer_suggester
# streamlit run app/app.py

from src.config import (
    APP_TITLE,
    ensure_directories_exist,
)
from src.data_loader import load_demo_inputs
from src.soil_health_index import compute_soil_health
from src.fertilizer_rules import suggest_fertilizers
from src.recommendation_engine import build_final_recommendation


st.set_page_config(
    page_title=f"{APP_TITLE} – Soil Analysis & Demo",
    page_icon="📊",
    layout="wide",
)


def render_header():
    st.title("📊 Soil Analysis & Demo Scenarios")
    st.caption(
        "Use pre-defined soil test cases to explore how soil chemistry and crop choice "
        "influence fertilizer recommendations."
    )
    st.markdown("---")


def main():
    ensure_directories_exist()
    render_header()

    # Load demo inputs from CSV
    try:
        demo_df = load_demo_inputs()
    except FileNotFoundError as e:
        st.error(
            "Demo input file not found.\n\n"
            "Make sure `data/examples/demo_inputs.csv` exists."
        )
        st.stop()

    if demo_df.empty:
        st.warning("Demo dataset is empty. Add some rows to `demo_inputs.csv`.")
        st.stop()

    # Left: scenario selector
    col_left, col_right = st.columns([1.0, 2.0])

    with col_left:
        st.markdown("### 🔎 Choose a sample scenario")

        # Build nice labels for scenarios
        labels = []
        for idx, row in demo_df.iterrows():
            label = (
                f"Case {idx + 1}: "
                f"Crop = {row.get('crop', 'Unknown')}, "
                f"pH = {row.get('pH', '?')}, "
                f"N = {row.get('nitrogen', '?')}, "
                f"P = {row.get('phosphorus', '?')}, "
                f"K = {row.get('potassium', '?')}"
            )
            labels.append(label)

        selected_label = st.selectbox(
            "Select a demo soil–crop combination:",
            options=labels,
            index=0,
        )

        selected_index = labels.index(selected_label)
        selected_row = demo_df.iloc[selected_index]

        st.markdown("### 📄 Raw input values")
        st.write(selected_row.to_frame().T)

        st.info(
            "Tip: You can go back to the main page and manually type similar values "
            "in the form to compare with your own field data."
        )

    with col_right:
        st.markdown("### 🧪 Analysis of selected scenario")

        # Convert row to dict for backend functions
        input_data = selected_row.to_dict()

        # Safety: ensure types
        for key in ["pH", "organic_carbon", "nitrogen", "phosphorus", "potassium",
                    "rainfall", "temperature", "ec"]:
            if key in input_data:
                try:
                    input_data[key] = float(input_data[key])
                except (TypeError, ValueError):
                    pass

        # 1) Soil health
        soil_health = compute_soil_health(input_data)

        idx = soil_health.get("index", None)
        cat = soil_health.get("category", "Unknown")

        if idx is not None:
            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Soil Health Index (0–1)", f"{idx:.2f}")
            with c2:
                st.success(f"Overall category: {cat}")
        else:
            st.info("Could not compute soil health index.")

        with st.expander("Factor-wise soil health details"):
            factors = soil_health.get("factor_scores", {})
            for key, info in factors.items():
                score = info.get("score", 0.0)
                level = info.get("level", "unknown")
                msg = info.get("message", "")
                st.markdown(f"**{key.upper()}** – score: `{score:.2f}`, level: `{level}`")
                st.write(msg)
                st.markdown("---")

        st.markdown("---")

        # 2) Rule-based recs directly
        crop = str(input_data.get("crop", ""))
        rules_out = suggest_fertilizers(soil_data=input_data, crop=crop)

        st.markdown("### 📐 Rule-based fertilizer suggestions")
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

        recs = rules_out.get("primary_recommendations", [])
        if recs:
            st.markdown("**Fertilizers suggested by rules:**")
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
            st.info("No rule-based recommendations for this case.")

        warnings = rules_out.get("warnings", [])
        notes = rules_out.get("notes", [])

        if warnings:
            st.markdown("**⚠️ Warnings:**")
            for w in warnings:
                st.warning(w)

        if notes:
            st.markdown("**📝 Notes:**")
            for n in notes:
                st.info(n)

        st.markdown("---")

        # 3) Full hybrid engine (rules + ML)
        st.markdown("### 🤝 Hybrid engine (ML + rules)")
        result = build_final_recommendation(input_data)
        final_choice = result.get("final_choice", {})
        ml_out = result.get("ml", {})

        name = final_choice.get("name")
        source = final_choice.get("source", "none")
        rationale = final_choice.get("rationale", "")

        source_label = {
            "ml+rules": "ML + Rule-based (both agree)",
            "ml_only": "ML-only (data-driven)",
            "rules_only": "Rule-based agronomy",
            "none": "Unknown",
        }.get(source, source)

        if name is not None:
            st.success(f"Final recommended fertilizer: `{name}`")
            st.caption(f"Decision source: {source_label}")
            st.markdown("**Rationale:**")
            st.write(rationale)
        else:
            st.error(
                "Hybrid engine could not produce a clear final recommendation for this case."
            )

        # Show ML probabilities if available
        if ml_out.get("available", False) and ml_out.get("probabilities"):
            st.markdown("**ML class probabilities:**")
            probs = ml_out["probabilities"]
            sorted_items = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            for label, p in sorted_items:
                st.write(f"- `{label}` → {p:.2%}")
        elif not ml_out.get("available", False) and ml_out.get("message"):
            st.info(ml_out["message"])


if __name__ == "__main__":
    main()
