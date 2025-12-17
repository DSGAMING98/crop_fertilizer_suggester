import sys
from pathlib import Path

# Make sure Python can see the project root (where `src` lives)
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.config import (
    APP_TITLE,
    FERTILIZER_NUTRIENT_PROFILE,
    ensure_directories_exist,
)

try:
    from src.data_loader import load_fertilizer_db
except Exception:
    load_fertilizer_db = None



st.set_page_config(
    page_title=f"{APP_TITLE} – Fertilizer Solutions",
    page_icon="🧪",
    layout="wide",
)


def render_header():
    st.title("🧪 Fertilizer Solutions & Nutrient Calculator")
    st.caption(
        "Explore fertilizer compositions, chemistry, and calculate how much to apply "
        "for a given N–P–K requirement."
    )
    st.markdown("---")


def get_fertilizer_dataframe():
    """
    Try loading fertilizer_db.csv via data_loader.
    If not available, fall back to FERTILIZER_NUTRIENT_PROFILE dict.
    """
    import pandas as pd

    df = None
    if load_fertilizer_db is not None:
        try:
            df = load_fertilizer_db()
        except FileNotFoundError:
            df = None

    if df is None or df.empty:
        # Build from config dict
        rows = []
        for name, info in FERTILIZER_NUTRIENT_PROFILE.items():
            rows.append(
                {
                    "name": name,
                    "N_pct": info.get("N", 0.0),
                    "P_pct": info.get("P", 0.0),
                    "K_pct": info.get("K", 0.0),
                    "S_pct": info.get("S", 0.0),
                    "type": info.get("type", "Unknown"),
                    "notes": info.get("notes", ""),
                }
            )
        if rows:
            df = pd.DataFrame(rows)
    return df


def pick_fertilizer(df):
    st.markdown("### 🔍 Select a fertilizer")

    if df is not None and "name" in df.columns:
        options = sorted(df["name"].unique().tolist())
    else:
        options = sorted(list(FERTILIZER_NUTRIENT_PROFILE.keys()))

    if not options:
        st.error("No fertilizer data available.")
        return None, {}

    selected_name = st.selectbox("Fertilizer", options=options, index=0)

    # Get details
    fert_info = {}
    if df is not None and "name" in df.columns:
        subset = df[df["name"] == selected_name]
        if not subset.empty:
            row = subset.iloc[0]
            fert_info = {
                "name": selected_name,
                "type": row.get("type", "Unknown"),
                "N_pct": float(row.get("N_pct", 0.0)),
                "P_pct": float(row.get("P_pct", 0.0)),
                "K_pct": float(row.get("K_pct", 0.0)),
                "S_pct": float(row.get("S_pct", 0.0)),
                "notes": row.get("notes", ""),
            }
    if not fert_info and selected_name in FERTILIZER_NUTRIENT_PROFILE:
        cfg = FERTILIZER_NUTRIENT_PROFILE[selected_name]
        fert_info = {
            "name": selected_name,
            "type": cfg.get("type", "Unknown"),
            "N_pct": float(cfg.get("N", 0.0)),
            "P_pct": float(cfg.get("P", 0.0)),
            "K_pct": float(cfg.get("K", 0.0)),
            "S_pct": float(cfg.get("S", 0.0)),
            "notes": cfg.get("notes", ""),
        }

    return selected_name, fert_info


def render_fertilizer_details(fert_info: dict):
    if not fert_info:
        st.info("Select a fertilizer to see its composition and chemistry notes.")
        return

    st.markdown("### 🧬 Fertilizer composition & chemistry")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Name:** `{fert_info.get('name', 'Unknown')}`")
        st.markdown(f"**Type:** `{fert_info.get('type', 'Unknown')}`")

        st.markdown("**Nutrient content (%):**")
        st.write(
            {
                "N": fert_info.get("N_pct", 0.0),
                "P (as P₂O₅)": fert_info.get("P_pct", 0.0),
                "K (as K₂O)": fert_info.get("K_pct", 0.0),
                "S": fert_info.get("S_pct", 0.0),
            }
        )

    with col2:
        notes = fert_info.get("notes", "")
        if notes:
            st.markdown("**Agronomic / chemistry notes:**")
            st.write(notes)
        else:
            st.caption("No additional notes available for this fertilizer.")


def compute_required_fertilizer_kg(
    target_n: float,
    target_p: float,
    target_k: float,
    fert_n_pct: float,
    fert_p_pct: float,
    fert_k_pct: float,
):
    """
    Very simple one-fertilizer calculator:
    Given target extra N, P, K (kg/ha) and fertilizer percentages,
    compute how many kg/ha are needed to at least satisfy the greatest
    requirement without going under on any positive target.

    Returns:
        (recommended_kg_per_ha, supplied_N, supplied_P, supplied_K)
    """
    # Convert % to fraction
    n_frac = fert_n_pct / 100.0 if fert_n_pct else 0.0
    p_frac = fert_p_pct / 100.0 if fert_p_pct else 0.0
    k_frac = fert_k_pct / 100.0 if fert_k_pct else 0.0

    needed_kg = []

    if target_n > 0 and n_frac > 0:
        needed_kg.append(target_n / n_frac)
    if target_p > 0 and p_frac > 0:
        needed_kg.append(target_p / p_frac)
    if target_k > 0 and k_frac > 0:
        needed_kg.append(target_k / k_frac)

    if not needed_kg:
        return 0.0, 0.0, 0.0, 0.0

    kg_per_ha = max(needed_kg)

    supplied_n = kg_per_ha * n_frac
    supplied_p = kg_per_ha * p_frac
    supplied_k = kg_per_ha * k_frac

    return kg_per_ha, supplied_n, supplied_p, supplied_k


def render_calculator(fert_info: dict):
    st.markdown("### 📏 N–P–K requirement calculator (single fertilizer)")

    if not fert_info:
        st.info("Select a fertilizer first to use the calculator.")
        return

    with st.form("fert_req_form"):
        st.caption("Enter how much additional N, P₂O₅ and K₂O the soil–crop system needs (kg/ha).")
        col1, col2, col3 = st.columns(3)

        with col1:
            target_n = st.number_input(
                "Target extra N (kg/ha)",
                min_value=0.0,
                max_value=300.0,
                value=50.0,
                step=5.0,
            )
        with col2:
            target_p = st.number_input(
                "Target extra P₂O₅ (kg/ha)",
                min_value=0.0,
                max_value=200.0,
                value=20.0,
                step=5.0,
            )
        with col3:
            target_k = st.number_input(
                "Target extra K₂O (kg/ha)",
                min_value=0.0,
                max_value=300.0,
                value=0.0,
                step=5.0,
            )

        submitted = st.form_submit_button("💡 Calculate fertilizer dose")

    if not submitted:
        return

    fert_n = fert_info.get("N_pct", 0.0)
    fert_p = fert_info.get("P_pct", 0.0)
    fert_k = fert_info.get("K_pct", 0.0)

    if all(v == 0 for v in [target_n, target_p, target_k]):
        st.info("All targets are zero. No fertilizer is required in this simple calculation.")
        return

    if fert_n == fert_p == fert_k == 0:
        st.error("Selected fertilizer has 0% N, P and K – cannot use for NPK requirement.")
        return

    kg_per_ha, sup_n, sup_p, sup_k = compute_required_fertilizer_kg(
        target_n, target_p, target_k, fert_n, fert_p, fert_k
    )

    st.success(
        f"Recommended application rate: **{kg_per_ha:.1f} kg/ha** of `{fert_info.get('name')}` "
        f"(based on highest N/P/K requirement)."
    )

    st.markdown("**Approximate nutrients supplied at this dose:**")
    st.write(
        {
            "N supplied (kg/ha)": round(sup_n, 1),
            "P₂O₅ supplied (kg/ha)": round(sup_p, 1),
            "K₂O supplied (kg/ha)": round(sup_k, 1),
        }
    )

    # Simple educational note
    st.info(
        "This is a simplified one-fertilizer calculation. In real agronomy, N, P and K are often "
        "balanced using a combination of fertilizers and organic sources."
    )


def main():
    ensure_directories_exist()
    render_header()

    df = get_fertilizer_dataframe()

    col_left, col_right = st.columns([1.1, 1.9])

    with col_left:
        selected_name, fert_info = pick_fertilizer(df)
        render_fertilizer_details(fert_info)

    with col_right:
        render_calculator(fert_info)

        st.markdown("---")
        if df is not None:
            st.markdown("### 📚 All fertilizers database (for browsing)")
            st.dataframe(df, use_container_width=True)
        else:
            st.caption("No full fertilizer database available – using only built-in profiles.")


if __name__ == "__main__":
    main()
