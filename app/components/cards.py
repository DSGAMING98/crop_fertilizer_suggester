from __future__ import annotations

from typing import Dict, Optional

import streamlit as st


def info_card(title: str, body: str, emoji: str = "", color: str = "#1e8449"):
    """
    Simple info card with title + body in a styled container.
    """
    icon = f"{emoji} " if emoji else ""
    st.markdown(
        f"""
        <div style="
            border-radius: 16px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.6rem;
            background: #ffffff;
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 8px 18px rgba(0,0,0,0.03);
        ">
            <div style="font-weight: 600; font-size: 0.98rem; color: {color}; margin-bottom: 0.25rem;">
                {icon}{title}
            </div>
            <div style="font-size: 0.9rem; color: #333333;">
                {body}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill_badge(text: str, bg: str = "#e8f5e9", fg: str = "#1e8449", size: str = "0.75rem"):
    """
    Small pill badge – can be used inside st.markdown or on its own.
    """
    st.markdown(
        f"""
        <span style="
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            background: {bg};
            color: {fg};
            font-size: {size};
            font-weight: 600;
            letter-spacing: 0.02em;
        ">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def soil_health_card(soil_health: Dict):
    """
    Compact card summarising soil health index and category.
    Expects dict from soil_health_index.compute_soil_health_index().
    """
    idx = soil_health.get("index", None)
    cat = soil_health.get("category", "Unknown")

    if idx is None:
        info_card("Soil health", "Soil health index could not be computed.")
        return

    factors = soil_health.get("factor_scores", {})

    st.markdown(
        """
        <div style="
            border-radius: 18px;
            padding: 1.0rem 1.1rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(135deg, #e8f5e9, #ffffff);
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 10px 24px rgba(0,0,0,0.04);
        ">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 0.4rem;">
            <div style="font-weight:700; font-size: 1.0rem; color:#145a32;">
                🌍 Soil health summary
            </div>
            <div style="
                padding: 0.2rem 0.7rem;
                border-radius: 999px;
                background:#145a32;
                color:white;
                font-size:0.8rem;
                font-weight:600;
            ">
                Index: {idx:.2f} • {cat}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Factor mini-lines
    lines = []
    for key, info in factors.items():
        level = info.get("level", "unknown")
        lines.append(f"{key.upper()}: {level}")

    if lines:
        st.markdown(
            "<div style='font-size:0.85rem; color:#1b4332;'>"
            + " | ".join(lines)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def fertilizer_reco_card(
    fert_name: Optional[str],
    source_label: str,
    rationale: str,
):
    """
    Card for final fertilizer recommendation.
    """
    if fert_name is None:
        info_card(
            title="No clear fertilizer recommendation",
            body=(
                "The system could not determine a single best fertilizer. "
                "Please verify soil data or combine recommendations with local guidelines."
            ),
            emoji="⚠️",
            color="#b03a2e",
        )
        return

    st.markdown(
        """
        <div style="
            border-radius: 18px;
            padding: 1.0rem 1.1rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(135deg, #e3f2fd, #ffffff);
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 12px 28px rgba(0,0,0,0.04);
        ">
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="font-weight: 700; font-size: 1.0rem; color:#0d47a1; margin-bottom: 0.3rem;">
            ✅ Recommended fertilizer
        </div>
        <div style="font-size: 1.1rem; font-weight: 700; color:#1a237e; margin-bottom: 0.2rem;">
            {fert_name}
        </div>
        <div style="
            font-size: 0.78rem;
            font-weight: 600;
            color:#1565c0;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background:#e3f2fd;
            display:inline-block;
            margin-bottom: 0.4rem;
        ">
            Source: {source_label}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if rationale:
        st.markdown(
            f"""
            <div style="font-size:0.9rem; color:#263238;">
                {rationale}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
