from typing import Dict, Any

import pandas as pd

from .config import SOIL_HEALTH_THRESHOLDS, PH_BANDS



# HELPER SCORERS FOR EACH FACTOR


def _score_ph(pH: float) -> Dict[str, Any]:
    """
    Score soil pH based on general agronomic ranges.

    Returns dict with:
        score  : float between 0 and 1
        level  : text label
        message: explanation string
    """
    if pH is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "pH not provided; assuming medium soil reaction.",
        }

    if pH < PH_BANDS["strongly_acidic"][1]:
        return {
            "score": 0.3,
            "level": "strongly acidic",
            "message": (
                f"Soil pH ≈ {pH:.1f} (strongly acidic). Many crops struggle here; "
                "liming is usually recommended to raise pH closer to neutral."
            ),
        }
    elif pH < PH_BANDS["moderately_acidic"][1]:
        return {
            "score": 0.7,
            "level": "moderately acidic",
            "message": (
                f"Soil pH ≈ {pH:.1f} (moderately acidic). Suitable for acid-loving crops "
                "but you may still consider mild liming depending on crop."
            ),
        }
    elif pH < PH_BANDS["neutral"][1]:
        return {
            "score": 1.0,
            "level": "near neutral",
            "message": (
                f"Soil pH ≈ {pH:.1f} (near neutral). This is ideal for most field crops "
                "and maximizes nutrient availability."
            ),
        }
    elif pH < PH_BANDS["slightly_alkaline"][1]:
        return {
            "score": 0.7,
            "level": "slightly alkaline",
            "message": (
                f"Soil pH ≈ {pH:.1f} (slightly alkaline). Usually acceptable but some "
                "micronutrients (Fe, Zn) may become less available."
            ),
        }
    else:
        return {
            "score": 0.3,
            "level": "strongly alkaline",
            "message": (
                f"Soil pH ≈ {pH:.1f} (strongly alkaline). High pH can lock nutrients; "
                "consider acid-forming fertilizers or organic matter to buffer pH."
            ),
        }


def _score_organic_carbon(oc: float) -> Dict[str, Any]:
    """
    Score organic carbon (%) — rough generic ranges.
    """
    if oc is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "Organic carbon not provided; assuming moderate status.",
        }

    if oc < 0.5:
        return {
            "score": 0.4,
            "level": "low",
            "message": (
                f"Organic carbon ≈ {oc:.2f}% (low). Soil organic matter is poor; "
                "add FYM, compost, or green manures to improve structure and CEC."
            ),
        }
    elif oc < 0.75:
        return {
            "score": 0.7,
            "level": "medium",
            "message": (
                f"Organic carbon ≈ {oc:.2f}% (medium). Some organic matter present, "
                "but regular additions of organics will still help."
            ),
        }
    elif oc < 1.5:
        return {
            "score": 1.0,
            "level": "good",
            "message": (
                f"Organic carbon ≈ {oc:.2f}% (good). Soil has healthy organic matter; "
                "this supports microbial life and nutrient buffering."
            ),
        }
    else:
        return {
            "score": 0.9,
            "level": "very high",
            "message": (
                f"Organic carbon ≈ {oc:.2f}% (very high). Excellent organic matter; "
                "watch waterlogging and N immobilization for some crops."
            ),
        }


def _score_n(n: float) -> Dict[str, Any]:
    """
    Score available nitrogen (generic kg/ha style).
    """
    if n is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "Available nitrogen not provided; assuming medium status.",
        }

    if n < 50:
        return {
            "score": 0.4,
            "level": "low",
            "message": (
                f"Available N ≈ {n:.0f} (low). Nitrogen is likely limiting; "
                "N-rich fertilizers (e.g., urea, ammonium sulphate) are needed."
            ),
        }
    elif n < 150:
        return {
            "score": 1.0,
            "level": "adequate",
            "message": (
                f"Available N ≈ {n:.0f} (adequate). Nitrogen is generally sufficient "
                "for many crops under normal yield targets."
            ),
        }
    else:
        return {
            "score": 0.6,
            "level": "high",
            "message": (
                f"Available N ≈ {n:.0f} (high). Excessive N can cause lush vegetative "
                "growth, lodging, and environmental losses; avoid over-application."
            ),
        }


def _score_p(p: float) -> Dict[str, Any]:
    """
    Score available phosphorus.
    """
    if p is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "Available phosphorus not provided; assuming medium status.",
        }

    if p < 15:
        return {
            "score": 0.4,
            "level": "low",
            "message": (
                f"Available P ≈ {p:.0f} (low). Phosphorus deficiency may limit root "
                "growth; phosphatic fertilizers like DAP/SSP are recommended."
            ),
        }
    elif p < 60:
        return {
            "score": 1.0,
            "level": "adequate",
            "message": (
                f"Available P ≈ {p:.0f} (adequate). Phosphorus is generally in the "
                "optimal range for most crops."
            ),
        }
    else:
        return {
            "score": 0.6,
            "level": "high",
            "message": (
                f"Available P ≈ {p:.0f} (high). Very high P can reduce micronutrient "
                "uptake; avoid unnecessary P fertilization."
            ),
        }


def _score_k(k: float) -> Dict[str, Any]:
    """
    Score available potassium.
    """
    if k is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "Available potassium not provided; assuming medium status.",
        }

    if k < 50:
        return {
            "score": 0.4,
            "level": "low",
            "message": (
                f"Available K ≈ {k:.0f} (low). Potassium deficiency can affect "
                "drought tolerance and grain quality; potassic fertilizers are needed."
            ),
        }
    elif k < 200:
        return {
            "score": 1.0,
            "level": "adequate",
            "message": (
                f"Available K ≈ {k:.0f} (adequate). Potassium status is generally "
                "suitable for balanced nutrition."
            ),
        }
    else:
        return {
            "score": 0.7,
            "level": "high",
            "message": (
                f"Available K ≈ {k:.0f} (high). Over-supply rarely toxic but "
                "can disturb nutrient balance; avoid unnecessary K application."
            ),
        }


def _score_ec(ec: float) -> Dict[str, Any]:
    """
    Score electrical conductivity (dS/m) as a proxy for salinity.
    """
    if ec is None:
        return {
            "score": 0.5,
            "level": "unknown",
            "message": "Electrical conductivity not provided; assuming medium salinity.",
        }

    if ec < 0.8:
        return {
            "score": 1.0,
            "level": "non-saline",
            "message": (
                f"EC ≈ {ec:.2f} dS/m (non-saline). Salinity is not a major constraint "
                "for most crops."
            ),
        }
    elif ec < 2.0:
        return {
            "score": 0.7,
            "level": "slightly saline",
            "message": (
                f"EC ≈ {ec:.2f} dS/m (slightly saline). Some sensitive crops may be "
                "affected; choose tolerant varieties and manage irrigation."
            ),
        }
    else:
        return {
            "score": 0.3,
            "level": "saline",
            "message": (
                f"EC ≈ {ec:.2f} dS/m (saline). High salinity can strongly reduce "
                "germination and yield; leaching and gypsum/organic matter may help."
            ),
        }



# OVERALL SOIL HEALTH INDEX


def _categorize_soil_health(index: float) -> str:
    """
    Convert numeric index (0–1) into category label using thresholds from config.
    """
    thr = SOIL_HEALTH_THRESHOLDS
    if index >= thr["excellent"]:
        return "Excellent"
    elif index >= thr["good"]:
        return "Good"
    elif index >= thr["moderate"]:
        return "Moderate"
    else:
        return "Poor"


def compute_soil_health(soil_data: Any) -> Dict[str, Any]:
    """
    Compute soil health index from basic soil parameters.

    Parameters
    ----------
    soil_data : dict or pd.Series or pd.DataFrame (single row)
        Must contain at least:
            pH, organic_carbon, nitrogen, phosphorus, potassium, ec

    Returns
    -------
    result : dict
        {
            "index": float between 0 and 1,
            "category": "Excellent" | "Good" | "Moderate" | "Poor",
            "factor_scores": {
                "pH": {...},
                "organic_carbon": {...},
                "nitrogen": {...},
                "phosphorus": {...},
                "potassium": {...},
                "ec": {...},
            }
        }
    """
    # Normalize input into a pandas Series (single row)
    if isinstance(soil_data, pd.DataFrame):
        if soil_data.shape[0] != 1:
            raise ValueError(
                "compute_soil_health expects a single-row DataFrame or a dict/Series."
            )
        row = soil_data.iloc[0]
    elif isinstance(soil_data, pd.Series):
        row = soil_data
    elif isinstance(soil_data, dict):
        row = pd.Series(soil_data)
    else:
        raise TypeError(
            "soil_data must be a dict, pandas Series, or single-row DataFrame."
        )

    # Extract values (may be missing)
    pH = row.get("pH", None)
    oc = row.get("organic_carbon", None)
    n = row.get("nitrogen", None)
    p = row.get("phosphorus", None)
    k = row.get("potassium", None)
    ec = row.get("ec", None)

    factor_scores = {
        "pH": _score_ph(pH),
        "organic_carbon": _score_organic_carbon(oc),
        "nitrogen": _score_n(n),
        "phosphorus": _score_p(p),
        "potassium": _score_k(k),
        "ec": _score_ec(ec),
    }

    # Average the numeric scores to get overall index
    numeric_scores = [info["score"] for info in factor_scores.values()]
    index = float(sum(numeric_scores) / len(numeric_scores))

    category = _categorize_soil_health(index)

    return {
        "index": index,
        "category": category,
        "factor_scores": factor_scores,
    }


if __name__ == "__main__":
    # Quick manual test with dummy data
    sample = {
        "pH": 6.8,
        "organic_carbon": 0.9,
        "nitrogen": 120,
        "phosphorus": 35,
        "potassium": 160,
        "ec": 0.6,
    }
    res = compute_soil_health(sample)
    print("Soil Health Index:", round(res["index"], 3))
    print("Category:", res["category"])
    for k, v in res["factor_scores"].items():
        print(f"\n{k} -> score={v['score']:.2f}, level={v['level']}")
        print("  ", v["message"])
