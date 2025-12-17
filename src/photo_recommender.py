from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class PhotoReco:
    crop_group: str
    main_fertilizer: str
    plan_steps: List[str]
    reasons: List[str]
    cautions: List[str]


def _crop_group(crop: str) -> str:
    c = (crop or "").strip().lower()

    cereals = ["rice", "wheat", "maize", "corn", "barley", "sorghum", "millet", "ragi"]
    pulses = ["gram", "chickpea", "lentil", "pea", "pigeon", "moong", "urad", "beans", "soy", "soybean"]
    oilseeds = ["groundnut", "peanut", "mustard", "sunflower", "sesame", "til", "castor"]
    cash = ["cotton", "sugarcane"]
    veggies = ["tomato", "potato", "onion", "chilli", "brinjal", "eggplant", "cabbage", "cauliflower", "okra"]

    if any(x in c for x in cereals):
        return "cereal"
    if any(x in c for x in pulses):
        return "pulse"
    if any(x in c for x in oilseeds):
        return "oilseed"
    if any(x in c for x in cash):
        return "cash_crop"
    if any(x in c for x in veggies):
        return "vegetable"
    return "general"


def recommend_from_soil_crop(soil_type: str, crop: str) -> Dict:
    """
    Photo-only fertilizer recommendation:
    Uses ONLY soil_type + crop (no NPK/pH).
    Output is a sensible plan: basal + top dressing + soil-based cautions.
    """
    soil = (soil_type or "").strip().lower()
    crop_name = crop or "Crop"
    group = _crop_group(crop_name)

    # Base templates (crop-driven)
    if group == "cereal":
        main = "Urea + DAP/SSP + MOP (split application)"
        steps = [
            "Basal dose: DAP or SSP at sowing/transplanting (supports root/early growth).",
            "Basal/early: MOP (potash) if crop is K-demanding or soil is light-textured.",
            "Top dressing: Urea in 2–3 split doses (cereals respond strongly to nitrogen).",
        ]
        reasons = [
            "Cereals need high nitrogen for vegetative growth + yield formation.",
            "Phosphorus supports root establishment and early vigor.",
            "Potassium improves water regulation and stress tolerance.",
        ]
        cautions = [
            "Avoid dumping all urea at once—splits reduce losses and improve uptake.",
        ]

        if "rice" in crop_name.lower():
            steps.insert(2, "For rice: keep urea splits aligned to tillering and panicle initiation stages.")
            cautions.append("In flooded rice, N losses can be high—splits + proper timing matter.")

    elif group == "pulse":
        main = "SSP/DAP + Biofertilizer (minimal urea)"
        steps = [
            "Basal dose: SSP or DAP (pulses need strong P for nodulation + roots).",
            "Seed/soil treatment: Rhizobium + PSB (biofertilizers) to improve N fixation + P availability.",
            "If plants look pale: very small starter N (low urea dose) only at early stage.",
        ]
        reasons = [
            "Pulses fix nitrogen using Rhizobium—too much urea reduces nodulation.",
            "Phosphorus drives root growth and energy transfer for nodules.",
        ]
        cautions = [
            "Do not overuse urea on pulses—it can reduce nitrogen fixation.",
        ]

    elif group == "oilseed":
        main = "SSP/DAP + MOP + moderate urea (balanced)"
        steps = [
            "Basal: SSP or DAP (oilseeds respond well to phosphorus).",
            "Add MOP if soil is light or crop is stress-prone.",
            "Urea: moderate split doses (avoid excess N which can reduce oil quality).",
        ]
        reasons = [
            "Balanced nutrition improves seed formation and oil content.",
        ]
        cautions = [
            "Excess nitrogen can increase vegetative growth and reduce oil percentage.",
        ]

    elif group == "cash_crop":
        main = "High K focus: MOP + split urea + DAP/SSP"
        steps = [
            "Basal: DAP/SSP for strong early rooting.",
            "Potash: MOP is important for quality (fiber in cotton, cane weight in sugarcane).",
            "Nitrogen: split urea applications across growth stages.",
        ]
        reasons = [
            "Cash crops often need strong potassium for quality and stress resistance.",
        ]
        cautions = [
            "Avoid single heavy nitrogen dose—split to reduce loss and lodging issues.",
        ]

    elif group == "vegetable":
        main = "Balanced NPK + organic manure (FYM/compost)"
        steps = [
            "Before planting: FYM/compost to improve soil structure and nutrient buffering.",
            "Basal: DAP/SSP + MOP depending on crop demand.",
            "Nitrogen: urea in frequent small splits (vegetables are responsive but sensitive to excess).",
        ]
        reasons = [
            "Vegetables need steady nutrition and good soil structure for uniform yield.",
        ]
        cautions = [
            "Over-urea can cause leafy growth with poor fruiting in some vegetables.",
        ]

    else:
        main = "Balanced NPK approach (DAP/SSP + MOP + split urea)"
        steps = [
            "Basal: DAP/SSP for phosphorus.",
            "Potash: MOP if soil is light-textured or crop is stress-prone.",
            "Nitrogen: urea in splits matched to growth stages.",
        ]
        reasons = [
            "Without lab data, balanced nutrition is safer than single-nutrient dosing.",
        ]
        cautions = [
            "Lab test values give the best accuracy—photo-only is general guidance.",
        ]

    # Soil modifiers (soil-driven)
    if "sandy" in soil:
        steps.append("Soil modifier (Sandy): apply fertilizers in smaller, more frequent splits + add FYM/compost.")
        cautions.append("Sandy soils leach nutrients fast—avoid heavy single doses, especially nitrogen.")
    elif "clay" in soil:
        steps.append("Soil modifier (Clay): ensure drainage; avoid heavy single N dose; prefer split applications.")
        cautions.append("Clay soils can waterlog—N losses can occur via denitrification.")
    elif "loam" in soil:
        steps.append("Soil modifier (Loam): standard split schedule works well; maintain organic matter.")
    elif "silty" in soil:
        steps.append("Soil modifier (Silty clay): watch waterlogging; split N; avoid over-application.")

    return {
        "crop_group": group,
        "main_fertilizer": main,
        "plan_steps": steps,
        "reasons": reasons,
        "cautions": cautions,
    }
