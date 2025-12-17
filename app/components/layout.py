from __future__ import annotations

from contextlib import contextmanager

import streamlit as st


def section_header(title: str, emoji: str = "", subtitle: str | None = None):
    """
    Standardised section header with optional subtitle.
    """
    icon = f"{emoji} " if emoji else ""
    st.markdown(
        f"""
        <div style="margin-top:0.2rem; margin-bottom:0.4rem;">
            <div style="font-size:1.0rem; font-weight:700; color:#1b4332;">
                {icon}{title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitle:
        st.caption(subtitle)


def soft_divider():
    """
    Light horizontal divider.
    """
    st.markdown(
        "<hr style='border:none; border-top:1px solid rgba(0,0,0,0.06); margin:0.6rem 0;' />",
        unsafe_allow_html=True,
    )


@contextmanager
def card_container():
    """
    Context manager for a generic card container:

    usage:
        with card_container():
            st.write("inside card")
    """
    st.markdown(
        """
        <div style="
            border-radius: 16px;
            background:#ffffff;
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 8px 20px rgba(0,0,0,0.03);
            padding: 0.9rem 1.0rem;
            margin-bottom: 0.8rem;
        ">
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


def two_column_layout(ratios=(1, 1)):
    """
    Quick helper to get two columns with a given ratio.

    Example:
        left, right = two_column_layout((1, 2))
        with left: ...
        with right: ...
    """
    return st.columns(ratios)
