from typing import Dict, Any, List

import pandas as pd

from .config import (
    FERTILIZER_NUTRIENT_PROFILE,
    PH_BANDS,
)



# HELPERS – INPUT NORMALIZATION


def _normalize_input(soil_data: Any) -> pd.Series:
    """
    Accept dict / Series / single-row DataFrame and return a pandas Series.
    """
    if isinstance(soil_data, pd.DataFrame):
        if soil_data.shape[0] != 1:
            raise ValueError(
                "Expected a single-row DataFrame for soil_data."
            )
        return soil_data.iloc[0]
    if isinstance(soil_data, pd.Series):
        return soil_data
    if isinstance(soil_data, dict):
        return pd.Series(soil_data)

    raise TypeError(
        "soil_data must be a dict, pandas Series, or single-row DataFrame."
    )



# BASIC NPK STATUS CLASSIFICATION
# (Simple generic thresholds; you can tune with real soil test norms)


def _status_n(n: float) -> str:
    if n is None:
        return "unknown"
    if n < 50:
        return "low"
    if n < 150:
        return "adequate"
    return "high"


def _status_p(p: float) -> str:
    if p is None:
        return "unknown"
    if p < 15:
        return "low"
    if p < 60:
        return "adequate"
    return "high"


def _status_k(k: float) -> str:
    if k is None:
        return "unknown"
    if k < 50:
        return "low"
    if k < 200:
        return "adequate"
    return "high"


def _ph_band_label(pH: float) -> str:
    if pH is None:
        return "unknown"

    if pH < PH_BANDS["strongly_acidic"][1]:
        return "strongly_acidic"
    if pH < PH_BANDS["moderately_acidic"][1]:
        return "moderately_acidic"
    if pH < PH_BANDS["neutral"][1]:
        return "neutral"
    if pH < PH_BANDS["slightly_alkaline"][1]:
        return "slightly_alkaline"
    return "strongly_alkaline"


# RULE-BASED FERTILIZER SUGGESTION


def _base_n_recommendations(n_status: str, ph_band: str) -> List[Dict[str, Any]]:
    """
    Decide nitrogenous fertilizers based on N status and pH.
    """
    recs: List[Dict[str, Any]] = []

    if n_status == "low":
        # Soil N low → need strong N source
        if ph_band in ("strongly_acidic", "moderately_acidic"):
            recs.append({
                "name": "Urea",
                "priority": 1,
                "reason": (
                    "Soil nitrogen is low and pH is on acidic side – urea provides "
                    "a high dose of N and has a relatively neutral reaction after "
                    "hydrolysis, suitable when combined with liming/organics."
                ),
            })
            recs.append({
                "name": "Ammonium Sulphate",
                "priority": 2,
                "reason": (
                    "Ammonium sulphate supplies N and sulphur. It is acid-forming, "
                    "so it fits better where mild acidification is acceptable or "
                    "where lime is also applied."
                ),
            })
        elif ph_band in ("slightly_alkaline", "strongly_alkaline"):
            recs.append({
                "name": "Urea",
                "priority": 1,
                "reason": (
                    "Soil nitrogen is low. Urea gives a concentrated N supply, but "
                    "in alkaline soils surface application can lose N as ammonia gas, "
                    "so incorporate into soil or irrigate after application."
                ),
            })
        else:
            recs.append({
                "name": "Urea",
                "priority": 1,
                "reason": (
                    "Nitrogen status is low and pH is near neutral. Urea is a "
                    "cost-effective high-N fertilizer in these conditions."
                ),
            })

    elif n_status == "adequate":
        recs.append({
            "name": "Urea",
            "priority": 3,
            "reason": (
                "Soil N is adequate. Only maintenance N doses are needed, so use "
                "urea in moderate, split applications matched to crop growth stages."
            ),
        })

    elif n_status == "high":
        recs.append({
            "name": "FYM",
            "priority": 4,
            "reason": (
                "Soil N is already high. Prefer organic manures and residue "
                "recycling over heavy mineral N doses to avoid lodging and losses."
            ),
        })

    return recs


def _base_p_recommendations(p_status: str, ph_band: str) -> List[Dict[str, Any]]:
    """
    Decide phosphatic fertilizers based on P status and pH.
    """
    recs: List[Dict[str, Any]] = []

    if p_status == "low":
        if ph_band in ("strongly_acidic", "moderately_acidic"):
            recs.append({
                "name": "SSP",
                "priority": 1,
                "reason": (
                    "Available P is low and soil is acidic. Single superphosphate "
                    "works well in acid soils and also supplies sulphur and calcium."
                ),
            })
            recs.append({
                "name": "DAP",
                "priority": 2,
                "reason": (
                    "DAP supplies both N and P. In acidic soils, apply near root "
                    "zone and avoid excessive use to reduce localised pH rise."
                ),
            })
        elif ph_band in ("slightly_alkaline", "strongly_alkaline"):
            recs.append({
                "name": "DAP",
                "priority": 1,
                "reason": (
                    "Available P is low in alkaline soils. DAP is a concentrated "
                    "source of P but should be placed, not broadcast, to reduce "
                    "fixation and improve root-zone availability."
                ),
            })
        else:
            recs.append({
                "name": "DAP",
                "priority": 1,
                "reason": (
                    "Available P is low and pH is around neutral. DAP provides "
                    "readily available P along with some N, ideal for basal dose."
                ),
            })

    elif p_status == "adequate":
        recs.append({
            "name": "DAP",
            "priority": 3,
            "reason": (
                "Phosphorus is adequate. Only small basal doses or starter "
                "phosphate are needed, especially for P-sensitive crops."
            ),
        })

    elif p_status == "high":
        recs.append({
            "name": "FYM",
            "priority": 4,
            "reason": (
                "High P soils generally do not need more phosphatic fertilizer. "
                "Use organic manures to maintain structure and micronutrient supply."
            ),
        })

    return recs


def _base_k_recommendations(k_status: str) -> List[Dict[str, Any]]:
    """
    Decide potassic fertilizers based on K status.
    """
    recs: List[Dict[str, Any]] = []

    if k_status == "low":
        recs.append({
            "name": "MOP",
            "priority": 1,
            "reason": (
                "Available K is low. Muriate of potash (MOP) is a standard K "
                "source; crucial for grain filling, disease resistance and "
                "drought tolerance."
            ),
        })
    elif k_status == "adequate":
        recs.append({
            "name": "MOP",
            "priority": 3,
            "reason": (
                "Potassium is adequate. Only maintenance doses are needed, "
                "especially for high-K-demand crops (sugarcane, potato, banana)."
            ),
        })
    elif k_status == "high":
        recs.append({
            "name": "FYM",
            "priority": 4,
            "reason": (
                "K is high; direct potassic fertilizers may be unnecessary. "
                "Organic manures help sustain overall fertility without excess K."
            ),
        })

    return recs


def _organic_and_bio_recommendations(oc: float) -> List[Dict[str, Any]]:
    """
    Suggest organic manures and biofertilizers based on organic carbon.
    """
    recs: List[Dict[str, Any]] = []

    if oc is None or oc < 0.75:
        recs.append({
            "name": "FYM",
            "priority": 1,
            "reason": (
                "Soil organic carbon is low to medium. Farmyard manure improves "
                "soil structure, microbial activity and long-term nutrient buffering."
            ),
        })
        recs.append({
            "name": "Vermicompost",
            "priority": 2,
            "reason": (
                "Vermicompost adds stable organic matter and slow-release nutrients, "
                "enhancing biological activity and root growth."
            ),
        })
    else:
        recs.append({
            "name": "Biofertilizer",
            "priority": 3,
            "reason": (
                "Organic carbon is reasonably good. Biofertilizers (Rhizobium, "
                "Azotobacter, PSB, etc.) can complement mineral fertilizers and "
                "improve nutrient-use efficiency."
            ),
        })

    return recs


def _crop_specific_adjustments(
    crop: str,
    npk_status: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    Add crop-specific tweaks: e.g., rice vs pulses vs vegetables.
    """
    crop = (crop or "").strip().lower()
    recs: List[Dict[str, Any]] = []

    # Rice – high N, flooded conditions
    if "rice" in crop:
        recs.append({
            "name": "Urea",
            "priority": 1,
            "reason": (
                "Rice is a high N-demand crop. Split urea applications aligned "
                "with tillering and panicle initiation stages are recommended."
            ),
        })
        if npk_status.get("K") == "low":
            recs.append({
                "name": "MOP",
                "priority": 2,
                "reason": (
                    "Potassium strongly influences rice lodging resistance and grain "
                    "quality; K application is important when soil K is low."
                ),
            })

    # Pulses – benefit from biological N fixation
    if "pulse" in crop or "gram" in crop or "lentil" in crop or "pea" in crop:
        recs.append({
            "name": "Biofertilizer",
            "priority": 1,
            "reason": (
                "Pulses form symbiosis with Rhizobium and related bacteria. "
                "Seed treatment and soil application with biofertilizers reduce "
                "the need for heavy mineral N doses."
            ),
        })
        if npk_status.get("P") == "low":
            recs.append({
                "name": "DAP",
                "priority": 2,
                "reason": (
                    "Adequate P is critical for nodulation and N fixation in pulses, "
                    "so a basal dose of DAP is useful when soil P is low."
                ),
            })

    # Vegetables – high nutrient demand, quality sensitive
    if "vegetable" in crop or crop in ("tomato", "potato", "chilli", "brinjal"):
        recs.append({
            "name": "NPK_17_17_17",
            "priority": 1,
            "reason": (
                "Vegetables are nutrient-intensive. Balanced complex fertilizers "
                "like NPK 17-17-17 help supply N, P and K in a single source."
            ),
        })
        recs.append({
            "name": "Vermicompost",
            "priority": 2,
            "reason": (
                "Vermicompost improves soil tilth and supports microbial activity, "
                "which is beneficial for root-heavy vegetable crops."
            ),
        })

    # Sugarcane – very high K and N demand
    if "sugarcane" in crop:
        recs.append({
            "name": "MOP",
            "priority": 1,
            "reason": (
                "Sugarcane removes large amounts of potassium; potash application "
                "is key for cane yield and juice quality."
            ),
        })
        recs.append({
            "name": "Urea",
            "priority": 2,
            "reason": (
                "High N requirement; split urea doses at formative and grand growth "
                "stages are recommended."
            ),
        })

    return recs



# MAIN PUBLIC FUNCTION


def suggest_fertilizers(
    soil_data: Any,
    crop: str,
) -> Dict[str, Any]:
    """
    Rule-based fertilizer suggestion engine.

    Parameters
    ----------
    soil_data : dict / Series / single-row DataFrame
        Must contain at least:
            pH, organic_carbon, nitrogen, phosphorus, potassium
    crop : str
        Name of the crop (for crop-specific tuning).

    Returns
    -------
    result : dict
        {
            "npk_status": {"N": str, "P": str, "K": str},
            "ph_band": str,
            "primary_recommendations": [ {name, reason, priority, nutrients}, ... ],
            "warnings": [str, ...],
            "notes": [str, ...],
        }
    """
    row = _normalize_input(soil_data)

    pH = row.get("pH", None)
    oc = row.get("organic_carbon", None)
    n = row.get("nitrogen", None)
    p = row.get("phosphorus", None)
    k = row.get("potassium", None)

    n_status = _status_n(n)
    p_status = _status_p(p)
    k_status = _status_k(k)
    ph_band = _ph_band_label(pH)

    npk_status = {"N": n_status, "P": p_status, "K": k_status}

    # Collect rule-based recs
    recs: List[Dict[str, Any]] = []
    recs.extend(_base_n_recommendations(n_status, ph_band))
    recs.extend(_base_p_recommendations(p_status, ph_band))
    recs.extend(_base_k_recommendations(k_status))
    recs.extend(_organic_and_bio_recommendations(oc))
    recs.extend(_crop_specific_adjustments(crop, npk_status))

    # Merge by fertilizer name: keep best (lowest priority number) and concat reasons
    combined: Dict[str, Dict[str, Any]] = {}
    for r in recs:
        name = r["name"]
        if name not in combined:
            combined[name] = {
                "name": name,
                "priority": r.get("priority", 99),
                "reasons": [r.get("reason", "")],
            }
        else:
            # Keep smallest priority (1 is highest)
            combined[name]["priority"] = min(
                combined[name]["priority"],
                r.get("priority", 99),
            )
            if r.get("reason"):
                combined[name]["reasons"].append(r["reason"])

    # Add nutrient profile info from config
    primary_recommendations: List[Dict[str, Any]] = []
    for fert_name, info in combined.items():
        profile = FERTILIZER_NUTRIENT_PROFILE.get(fert_name, {})
        primary_recommendations.append({
            "name": fert_name,
            "priority": info["priority"],
            "reasons": info["reasons"],
            "nutrients": profile,
        })

    # Sort by priority (ascending)
    primary_recommendations.sort(key=lambda x: x["priority"])

    # Warnings & notes
    warnings: List[str] = []
    notes: List[str] = []

    if n_status == "high":
        warnings.append(
            "Soil nitrogen is high – avoid excessive N doses to reduce lodging, "
            "nitrate leaching and greenhouse gas emissions."
        )
    if p_status == "high":
        warnings.append(
            "Soil phosphorus is high – further P application may be unnecessary and "
            "can aggravate micronutrient deficiencies."
        )
    if k_status == "high":
        notes.append(
            "Soil potassium is high – focus on balanced N and P along with organics "
            "instead of heavy K fertilization."
        )

    if ph_band in ("strongly_acidic", "moderately_acidic"):
        notes.append(
            "Soil is acidic – liming with materials like agricultural lime or dolomite "
            "is often recommended before intensive fertilization."
        )
    if ph_band in ("slightly_alkaline", "strongly_alkaline"):
        notes.append(
            "Soil is alkaline – avoid over-use of carbonate-rich or strongly basic "
            "materials; consider organic matter and acid-forming fertilizers where appropriate."
        )

    notes.append(
        "These recommendations are generic and should be fine-tuned using local soil "
        "test reports and crop-specific fertilizer schedules."
    )

    return {
        "npk_status": npk_status,
        "ph_band": ph_band,
        "primary_recommendations": primary_recommendations,
        "warnings": warnings,
        "notes": notes,
    }


if __name__ == "__main__":
    # Quick manual test
    sample_soil = {
        "pH": 6.2,
        "organic_carbon": 0.6,
        "nitrogen": 40,
        "phosphorus": 12,
        "potassium": 70,
    }
    result = suggest_fertilizers(sample_soil, crop="Rice")
    print("NPK status:", result["npk_status"])
    print("pH band:", result["ph_band"])
    print("\nRecommendations:")
    for r in result["primary_recommendations"]:
        print(f" - {r['name']} (priority {r['priority']})")
        print("   Nutrients:", r["nutrients"])
        for reason in r["reasons"]:
            print("    *", reason)
    print("\nWarnings:")
    for w in result["warnings"]:
        print(" -", w)
    print("\nNotes:")
    for n in result["notes"]:
        print(" -", n)
