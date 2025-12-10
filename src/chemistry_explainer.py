"""
Chemistry explainer module for the Crop-Fertilizer Suggestion System.

Provides structured content so the Streamlit page
`4_Chemistry_of_Fertilizers.py` can:

- Show topic cards (N, P, K, organics, biofertilizers, pH, soil health)
- Explain chemistry behind common fertilizers (Urea, DAP, SSP, MOP, NPK, FYM, Vermicompost)
- Generate small quiz-style Q&A for experiential learning
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .config import FERTILIZER_NUTRIENT_PROFILE


@dataclass
class FertilizerChemInfo:
    name: str
    type: str
    formula: str
    main_nutrient_form: str
    key_points: List[str]


@dataclass
class TopicSection:
    id: str
    title: str
    subtitle: str
    bullets: List[str]
    details: str



# CHEMISTRY TOPICS


def get_topic_sections() -> List[TopicSection]:
    """
    High-level chemistry topics to display as cards/expanders
    on the 'Chemistry of Fertilizers' page.
    """
    topics: List[TopicSection] = [
        TopicSection(
            id="nitrogenous",
            title="Nitrogenous fertilizers",
            subtitle="Sources of plant-available nitrogen (NH₄⁺ / NO₃⁻)",
            bullets=[
                "Urea, ammonium sulphate and related products supply N.",
                "Urea hydrolyses to ammonium, which then nitrifies to nitrate.",
                "Excess N can cause lodging, soft growth and environmental pollution.",
            ],
            details=(
                "Nitrogenous fertilizers primarily provide nitrogen in forms that plants can "
                "take up: ammonium (NH₄⁺) and nitrate (NO₃⁻). Urea [CO(NH₂)₂] is highly "
                "concentrated (46% N). In soil, it is hydrolysed by the enzyme urease to "
                "ammonium carbonate, which then converts to ammonium and nitrate. Ammonium "
                "sulphate [(NH₄)₂SO₄] supplies both N and sulphur, and has an acid-forming effect "
                "on soil. Proper timing, splitting doses and avoiding surface application on "
                "hot, dry soil help reduce volatilisation losses."
            ),
        ),
        TopicSection(
            id="phosphatic",
            title="Phosphatic fertilizers",
            subtitle="Supplying phosphorus for roots and energy transfer",
            bullets=[
                "DAP and SSP supply phosphorus as orthophosphate ions.",
                "P is key for root growth, early vigour and energy (ATP/ADP).",
                "Soil pH strongly affects P availability and fixation.",
            ],
            details=(
                "Phosphatic fertilizers supply P mainly in orthophosphate forms (H₂PO₄⁻, HPO₄²⁻). "
                "Diammonium phosphate (DAP) provides both N and P, whereas single superphosphate "
                "(SSP) provides P plus calcium and sulphur. P is relatively immobile in soil "
                "and tends to get fixed with Fe/Al in acidic soils and with Ca in alkaline soils. "
                "Band placement and correct pH management improve P use efficiency."
            ),
        ),
        TopicSection(
            id="potassic",
            title="Potassic fertilizers",
            subtitle="K⁺ for osmotic balance, stress tolerance and quality",
            bullets=[
                "MOP (KCl) is the most common K fertilizer.",
                "K regulates stomata, water use and stress resistance.",
                "Balanced K improves yield quality and disease resistance.",
            ],
            details=(
                "Potassic fertilizers mainly provide potassium as K⁺. Muriate of potash (MOP, KCl) "
                "contains about 60% K₂O equivalent. Potassium plays a central role in stomatal "
                "regulation, enzyme activation, and osmotic adjustment. Adequate K improves "
                "drought tolerance, disease resistance and quality parameters such as grain "
                "filling and sugar content."
            ),
        ),
        TopicSection(
            id="organics",
            title="Organic manures & composts",
            subtitle="Building soil organic matter and buffering capacity",
            bullets=[
                "FYM and vermicompost supply nutrients slowly over time.",
                "Organic matter improves soil structure and CEC.",
                "Combining organics with mineral fertilizers is ideal.",
            ],
            details=(
                "Organic manures such as farmyard manure (FYM) and vermicompost supply nutrients "
                "in slow-release forms, increase organic carbon and support beneficial soil life. "
                "They improve soil structure, porosity and water holding capacity, while raising "
                "the cation exchange capacity (CEC). Using organics along with chemical "
                "fertilizers buffers pH changes and leads to more sustainable fertility management."
            ),
        ),
        TopicSection(
            id="biofertilizers",
            title="Biofertilizers",
            subtitle="Using beneficial microbes to unlock soil nutrients",
            bullets=[
                "Rhizobium, Azotobacter, Azospirillum – biological N fixation.",
                "PSB – phosphate solubilising bacteria.",
                "Reduce dependence on high N/P chemical doses.",
            ],
            details=(
                "Biofertilizers are live microbial preparations that enhance the availability of "
                "nutrients. Rhizobium forms nodules on legumes and fixes atmospheric nitrogen, "
                "while free-living bacteria like Azotobacter and Azospirillum can fix N in the "
                "rhizosphere. Phosphate solubilising bacteria (PSB) release organic acids that "
                "solubilise fixed soil phosphorus. These reduce the need for heavy N and P inputs "
                "and support sustainable nutrient cycling."
            ),
        ),
        TopicSection(
            id="ph_and_availability",
            title="Soil pH & nutrient availability",
            subtitle="Why pH matters for fertilizer efficiency",
            bullets=[
                "Extreme acidity or alkalinity reduces availability of key nutrients.",
                "P is fixed by Fe/Al at low pH and by Ca at high pH.",
                "Micronutrient solubility changes strongly with pH.",
            ],
            details=(
                "Soil pH controls the chemical forms and solubility of many nutrients. Under acidic "
                "conditions, Al and Mn can become toxic and P may get fixed with Fe/Al oxides. In "
                "alkaline soils, micronutrients such as Fe, Zn and Mn become less available, and P "
                "can precipitate with Ca. Managing pH with amendments (lime, gypsum) and using "
                "appropriate fertilizer types greatly improves nutrient use efficiency."
            ),
        ),
        TopicSection(
            id="soil_health",
            title="Soil health & NPK balance",
            subtitle="Going beyond single nutrients to long-term fertility",
            bullets=[
                "Soil health includes pH, organic matter, NPK and biological activity.",
                "Overuse of one nutrient can disturb the balance and environment.",
                "Combining soil testing with balanced fertilization is essential.",
            ],
            details=(
                "Soil health is a holistic concept that includes chemical (pH, nutrients), physical "
                "(structure, porosity) and biological (microbes, fauna) components. Imbalanced "
                "application of NPK may give short-term yield but harm long-term health through "
                "acidification, salinity or nutrient mining. Regenerating soil organic matter and "
                "applying fertilizers as per soil test are key to sustainable productivity."
            ),
        ),
    ]
    return topics



# FERTILIZER-SPECIFIC CHEMISTRY


# Base info – chemistry-focused
_FERT_CHEM_BASE: Dict[str, FertilizerChemInfo] = {
    "Urea": FertilizerChemInfo(
        name="Urea",
        type="Nitrogenous",
        formula="CO(NH₂)₂",
        main_nutrient_form="Converts to NH₄⁺ → NO₃⁻ in soil",
        key_points=[
            "Highly concentrated N source (about 46% N).",
            "Hydrolysed by urease to ammonium carbonate, then to ammonium and nitrate.",
            "Surface application on hot, dry soil can cause NH₃ volatilisation.",
            "Best applied in split doses and incorporated into soil or irrigation water.",
        ],
    ),
    "DAP": FertilizerChemInfo(
        name="DAP (Diammonium phosphate)",
        type="Nitrogenous + Phosphatic",
        formula="(NH₄)₂HPO₄",
        main_nutrient_form="Provides NH₄⁺ and orthophosphate (HPO₄²⁻ / H₂PO₄⁻)",
        key_points=[
            "Supplies both N and P (commonly 18-46-0).",
            "Good as a starter fertilizer for many crops.",
            "Can locally raise pH near granule; take care in very acid soils.",
        ],
    ),
    "SSP": FertilizerChemInfo(
        name="SSP (Single superphosphate)",
        type="Phosphatic",
        formula="Ca(H₂PO₄)₂ + CaSO₄",
        main_nutrient_form="Provides soluble phosphate plus Ca²⁺ and SO₄²⁻",
        key_points=[
            "Supplies P along with calcium and sulphur.",
            "Slightly acidifying, useful in many neutral to alkaline soils.",
            "Often used in basal doses where S is also needed.",
        ],
    ),
    "MOP": FertilizerChemInfo(
        name="MOP (Muriate of potash)",
        type="Potassic",
        formula="KCl",
        main_nutrient_form="Provides K⁺ ions",
        key_points=[
            "Most common K fertilizer (about 60% K₂O equivalent).",
            "Improves stress tolerance, water use and quality of produce.",
            "Contains chloride; sensitive crops/soils may require careful use.",
        ],
    ),
    "NPK_17_17_17": FertilizerChemInfo(
        name="NPK 17-17-17",
        type="NPK complex",
        formula="Mixed complex fertilizer",
        main_nutrient_form="Balanced supply of N, P₂O₅ and K₂O",
        key_points=[
            "Each granule contains N, P and K in fixed ratio (17:17:17).",
            "Useful for balanced nutrition in high-value crops like vegetables.",
            "Less flexible than separate N, P, K sources for fine-tuning.",
        ],
    ),
    "FYM": FertilizerChemInfo(
        name="FYM (Farmyard manure)",
        type="Organic manure",
        formula="Mixture of decomposed dung, urine and bedding",
        main_nutrient_form="Slow-release N, P, K in organic forms",
        key_points=[
            "Low nutrient concentration but large benefits to soil structure.",
            "Increases organic carbon, CEC and microbial activity.",
            "Used regularly to maintain long-term soil health.",
        ],
    ),
    "Vermicompost": FertilizerChemInfo(
        name="Vermicompost",
        type="Organic manure",
        formula="Earthworm-processed organic matter",
        main_nutrient_form="Humus-rich material with moderate NPK",
        key_points=[
            "Produced by earthworms from organic residues.",
            "Improves root growth and seedling vigour.",
            "Often used in nurseries and high-value crops.",
        ],
    ),
}


def get_fertilizer_chemistry(name: str) -> Optional[FertilizerChemInfo]:
    """
    Return chemistry info for a fertilizer by name, if known.

    Matching is done case-insensitively and also supports
    common keys from FERTILIZER_NUTRIENT_PROFILE such as "NPK_17_17_17".
    """
    if not name:
        return None

    lower_name = name.lower()

    # Direct / approximate matching
    for key, info in _FERT_CHEM_BASE.items():
        if lower_name == key.lower():
            return info
        if key.lower() in lower_name or lower_name in key.lower():
            return info

    # Try matching against config keys (e.g. "NPK_17_17_17")
    for key in FERTILIZER_NUTRIENT_PROFILE.keys():
        if lower_name == key.lower():
            # If base chem available under that exact key, return it
            if key in _FERT_CHEM_BASE:
                return _FERT_CHEM_BASE[key]
            # else create a minimal info from config
            cfg = FERTILIZER_NUTRIENT_PROFILE[key]
            return FertilizerChemInfo(
                name=key,
                type=str(cfg.get("type", "Unknown")),
                formula="NPK fertilizer",
                main_nutrient_form="See N, P, K percentages",
                key_points=[
                    f"N: {cfg.get('N', 0)}%, P₂O₅: {cfg.get('P', 0)}%, K₂O: {cfg.get('K', 0)}%.",
                    "Complex fertilizer used for balanced NPK supply.",
                ],
            )
    return None



# MINI QUIZ / VIVA HELPERS


def get_quiz_items() -> List[Dict[str, str]]:
    """
    Returns a list of small Q&A items for viva / interactive use
    on the chemistry page.
    """
    return [
        {
            "question": "Why can urea cause nitrogen loss if left on the soil surface in hot, dry conditions?",
            "answer": (
                "Because during hydrolysis, carbonate and ammonium can form free ammonia gas (NH₃), "
                "which volatilises to the atmosphere if not incorporated into the soil or followed by irrigation."
            ),
        },
        {
            "question": "What is the advantage of SSP over DAP in sulphur-deficient soils?",
            "answer": (
                "SSP supplies phosphorus along with calcium and sulphur, making it useful where crops "
                "also need sulphur, whereas DAP does not supply S."
            ),
        },
        {
            "question": "How does soil pH influence phosphorus availability?",
            "answer": (
                "At low pH, P can be fixed by iron and aluminium oxides; at high pH, it can precipitate "
                "with calcium. Maximum availability typically occurs around mildly acidic to neutral pH."
            ),
        },
        {
            "question": "Why is potassium important for drought resistance?",
            "answer": (
                "K⁺ helps regulate stomatal opening and closing, improves osmotic adjustment and water-use efficiency, "
                "allowing plants to better tolerate water stress."
            ),
        },
        {
            "question": "What is the main role of biofertilizers in fertilizer management?",
            "answer": (
                "They use beneficial microbes to fix nitrogen or solubilise phosphorus, thereby increasing "
                "nutrient availability and reducing the need for high chemical fertilizer doses."
            ),
        },
    ]


__all__ = [
    "FertilizerChemInfo",
    "TopicSection",
    "get_topic_sections",
    "get_fertilizer_chemistry",
    "get_quiz_items",
]
