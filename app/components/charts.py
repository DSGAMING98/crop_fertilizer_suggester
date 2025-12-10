from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st


def npk_bar_chart(n_value: float, p_value: float, k_value: float, title: str = "N–P–K status"):
    """
    Show a simple bar chart of N, P, K values.
    """
    df = pd.DataFrame(
        {
            "Nutrient": ["N", "P", "K"],
            "Value": [n_value, p_value, k_value],
        }
    )
    st.markdown(f"#### 📊 {title}")
    st.bar_chart(df.set_index("Nutrient"))


def soil_health_radar_like(soil_health: Dict):
    """
    Fake radar-style view using a bar chart from factor scores.
    """
    factors = soil_health.get("factor_scores", {})
    if not factors:
        st.info("Soil health factor scores not available for chart.")
        return

    labels: List[str] = []
    scores: List[float] = []

    for key, info in factors.items():
        labels.append(key.upper())
        scores.append(float(info.get("score", 0.0)))

    df = pd.DataFrame({"Factor": labels, "Score": scores})
    st.markdown("#### 📊 Soil health factor scores")
    st.bar_chart(df.set_index("Factor"))


def fertilizer_probability_chart(probs: Dict[str, float]):
    """
    Show class probabilities from ML model as a horizontal bar chart.
    """
    if not probs:
        st.info("No class probability data available.")
        return

    items = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    df = pd.DataFrame(
        {
            "Fertilizer": labels,
            "Probability": values,
        }
    )

    st.markdown("#### 📊 ML class probabilities")
    st.bar_chart(df.set_index("Fertilizer"))
