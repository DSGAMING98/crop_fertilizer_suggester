import sys
from pathlib import Path

# Make sure Python can see project root (where `src` lives)
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from src.config import (
    APP_TITLE,
    FERTILIZER_NUTRIENT_PROFILE,
    ensure_directories_exist,
)
from src.chemistry_explainer import (
    get_topic_sections,
    get_fertilizer_chemistry,
    get_quiz_items,
)


st.set_page_config(
    page_title=f"{APP_TITLE} – Chemistry of Fertilizers",
    page_icon="🧬",
    layout="wide",
)


def render_header():
    st.title("🧬 Chemistry of Fertilizers")
    st.caption(
        "Concept explainer: connect N–P–K fertilizers, organic manures and biofertilizers "
        "with soil chemistry and plant nutrition."
    )
    st.markdown("---")


def render_fertilizer_lookup():
    st.markdown("### 🔍 Fertilizer chemistry lookup")

    fert_names = sorted(list(FERTILIZER_NUTRIENT_PROFILE.keys()))
    if not fert_names:
        st.info("No fertilizers found in configuration.")
        return

    selected = st.selectbox(
        "Choose a fertilizer to see its chemistry:",
        options=fert_names,
        index=0,
    )

    chem_info = get_fertilizer_chemistry(selected)

    if chem_info is None:
        st.warning(
            "No detailed chemistry record found for this fertilizer. "
            "Check the configuration or add it to chemistry_explainer.py."
        )
        return

    st.markdown(f"**Name:** `{chem_info.name}`")
    st.markdown(f"**Type:** `{chem_info.type}`")
    st.markdown(f"**Chemical formula (typical):** `{chem_info.formula}`")
    st.markdown(f"**Main nutrient form in soil/plant:** {chem_info.main_nutrient_form}")

    st.markdown("**Key points:**")
    for p in chem_info.key_points:
        st.markdown(f"- {p}")


def render_topics():
    st.markdown("### 📚 Key chemistry topics")

    topics = get_topic_sections()
    for topic in topics:
        with st.expander(f"{topic.title} – {topic.subtitle}"):
            st.markdown("**Main ideas:**")
            for b in topic.bullets:
                st.markdown(f"- {b}")
            st.markdown("")
            st.markdown("**Explanation:**")
            st.write(topic.details)


def render_quiz():
    st.markdown("### Quick Questions")

    items = get_quiz_items()
    if not items:
        st.caption("No quiz items defined.")
        return

    for i, qa in enumerate(items, start=1):
        q = qa.get("question", "").strip()
        a = qa.get("answer", "").strip()
        if not q:
            continue
        with st.expander(f"Q{i}. {q}"):
            if a:
                st.write(a)
            else:
                st.write("No answer text defined.")


def main():
    ensure_directories_exist()
    render_header()

    col_left, col_right = st.columns([1.0, 2.0])

    with col_left:
        render_fertilizer_lookup()

    with col_right:
        render_topics()

    st.markdown("---")
    render_quiz()


if __name__ == "__main__":
    main()
