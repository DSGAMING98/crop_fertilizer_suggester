from typing import Dict, Any, Optional

import numpy as np
import joblib

from .config import MODEL_FILE
from .preprocess import (
    build_input_dataframe_from_dict,
    load_preprocessor,
)
from .soil_health_index import compute_soil_health
from .fertilizer_rules import suggest_fertilizers



# MODEL LOADING


def load_model(path=MODEL_FILE):
    """
    Load the trained ML model from disk.

    Returns
    -------
    model : Any

    Raises
    ------
    FileNotFoundError
        If the model file does not exist.
    """
    return joblib.load(path)


# ML PREDICTION LAYER


def predict_fertilizer_ml(
    input_data: Dict[str, Any],
    model: Optional[Any] = None,
    preprocessor: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Use the ML model (if available) to predict a fertilizer.

    Parameters
    ----------
    input_data : dict
        Must contain all INPUT_FEATURES needed by the preprocessor.
    model : optional
        Preloaded model. If None, this function will attempt to load from disk.
    preprocessor : optional
        Preloaded preprocessor. If None, this function will attempt to load from disk.

    Returns
    -------
    result : dict
        {
            "available": bool,
            "predicted_fertilizer": str | None,
            "probabilities": dict | None,
            "message": str | None,
        }
    """
    # Try to load model if not provided
    if model is None:
        try:
            model = load_model()
        except FileNotFoundError:
            return {
                "available": False,
                "predicted_fertilizer": None,
                "probabilities": None,
                "message": (
                    "ML model file not found. Only rule-based recommendations "
                    "will be used."
                ),
            }

    # Try to load preprocessor if not provided
    if preprocessor is None:
        try:
            preprocessor = load_preprocessor()
        except FileNotFoundError:
            return {
                "available": False,
                "predicted_fertilizer": None,
                "probabilities": None,
                "message": (
                    "Preprocessor (scaler/encoder) file not found. Only rule-based "
                    "recommendations will be used."
                ),
            }

    # Build input dataframe
    try:
        df_input = build_input_dataframe_from_dict(input_data)
    except Exception as e:
        return {
            "available": False,
            "predicted_fertilizer": None,
            "probabilities": None,
            "message": f"Invalid input for ML model: {e}",
        }

    # Transform features
    try:
        X_transformed = preprocessor.transform(df_input)
    except Exception as e:
        return {
            "available": False,
            "predicted_fertilizer": None,
            "probabilities": None,
            "message": f"Error while transforming features: {e}",
        }

    # Predict
    try:
        y_pred = model.predict(X_transformed)
        predicted = str(y_pred[0])
    except Exception as e:
        return {
            "available": False,
            "predicted_fertilizer": None,
            "probabilities": None,
            "message": f"Error during ML prediction: {e}",
        }

    # Probabilities (if classifier supports it)
    prob_dict = None
    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(X_transformed)[0]
            classes = getattr(model, "classes_", None)
            if classes is not None:
                prob_dict = {
                    str(label): float(p)
                    for label, p in zip(classes, probs)
                }
        except Exception:
            prob_dict = None

    return {
        "available": True,
        "predicted_fertilizer": predicted,
        "probabilities": prob_dict,
        "message": None,
    }



# FINAL HYBRID RECOMMENDATION ENGINE


def build_final_recommendation(
    input_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Combine:
      - soil health index
      - rule-based fertilizer suggestions
      - (optional) ML prediction

    Parameters
    ----------
    input_data : dict
        Must at least include:
            pH, organic_carbon, nitrogen, phosphorus, potassium,
            soil_type, rainfall, temperature, ec, crop

    Returns
    -------
    result : dict
        {
            "input": {...},
            "soil_health": {...},
            "rules": {...},
            "ml": {...},
            "final_choice": {
                "name": str | None,
                "source": str,  # "rules_only" | "ml_only" | "ml+rules" | "none"
                "rationale": str,
            },
        }
    """
    # Basic safety
    input_copy = dict(input_data)  # shallow copy

    crop = str(input_copy.get("crop", "")).strip()

    # 1) Soil health analysis
    soil_health = compute_soil_health(input_copy)

    # 2) Rule-based fertilizer suggestions
    rules_out = suggest_fertilizers(soil_data=input_copy, crop=crop)

    # 3) ML prediction (if model/preprocessor exist)
    ml_out = predict_fertilizer_ml(input_copy)

    final_name: Optional[str] = None
    final_source: str = "none"
    rationale_lines = []

    # Decide final choice logic:
    # Priority: ML prediction if available, cross-checked with rules
    if ml_out.get("available", False) and ml_out.get("predicted_fertilizer"):
        ml_name = ml_out["predicted_fertilizer"]

        # See if ML prediction exists in rule list
        rule_match = None
        for r in rules_out.get("primary_recommendations", []):
            if r["name"] == ml_name:
                rule_match = r
                break

        final_name = ml_name

        if rule_match:
            final_source = "ml+rules"
            rationale_lines.append(
                f"ML model predicts '{ml_name}' as the most suitable fertilizer "
                f"for the given soil and crop."
            )
            rationale_lines.append(
                "Rule-based agronomic logic ALSO supports this choice based on "
                "soil NPK status and pH."
            )
            # Combine reasons from rules
            for reason in rule_match.get("reasons", []):
                rationale_lines.append(f"- {reason}")
        else:
            final_source = "ml_only"
            rationale_lines.append(
                f"ML model predicts '{ml_name}' as the best match based on patterns "
                f"learned from the training dataset."
            )
            rationale_lines.append(
                "Rule-based system does not have a direct matching primary "
                "recommendation with the same name, so treat this as a data-driven "
                "suggestion and cross-check with local recommendations."
            )
    else:
        # No ML available → fall back to highest-priority rule-based recommendation
        rule_recs = rules_out.get("primary_recommendations", [])
        if rule_recs:
            best = rule_recs[0]
            final_name = best["name"]
            final_source = "rules_only"
            rationale_lines.append(
                f"Using rule-based agronomic logic, '{final_name}' is selected as "
                f"the most suitable fertilizer for the current soil and crop."
            )
            for reason in best.get("reasons", []):
                rationale_lines.append(f"- {reason}")
        else:
            final_name = None
            final_source = "none"
            rationale_lines.append(
                "No clear fertilizer recommendation could be generated from the "
                "rule-based system, and ML model is not available."
            )

    # Add soil-health perspective
    sh_index = soil_health.get("index", None)
    sh_cat = soil_health.get("category", None)
    if sh_index is not None and sh_cat is not None:
        rationale_lines.append(
            f"Soil Health Index is {sh_index:.2f} ({sh_cat}). Fertilizer use should "
            f"aim to improve or maintain this level while avoiding over-application."
        )

    # If ML is unavailable, mention once (for UX)
    if not ml_out.get("available", False) and ml_out.get("message"):
        rationale_lines.append(
            f"Note: {ml_out['message']}"
        )

    final_choice = {
        "name": final_name,
        "source": final_source,
        "rationale": "\n".join(rationale_lines),
    }

    return {
        "input": input_copy,
        "soil_health": soil_health,
        "rules": rules_out,
        "ml": ml_out,
        "final_choice": final_choice,
    }


if __name__ == "__main__":
    # Quick manual test
    sample_input = {
        "pH": 6.4,
        "organic_carbon": 0.7,
        "nitrogen": 55,
        "phosphorus": 18,
        "potassium": 120,
        "soil_type": "Loam",
        "rainfall": 800,
        "temperature": 27,
        "ec": 0.6,
        "crop": "Rice",
    }
    result = build_final_recommendation(sample_input)
    print("Final choice:", result["final_choice"])
    print("\nRationale:\n", result["final_choice"]["rationale"])
