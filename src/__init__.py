"""
src package for Crop-Fertilizer Suggestion System.

Holds:
- config.py                # paths, constants, fertilizer profiles
- data_loader.py           # CSV loaders
- preprocess.py            # scaler + encoder + input builder
- soil_health_index.py     # soil health index & explanations
- fertilizer_rules.py      # rule-based agronomic logic
- recommendation_engine.py # hybrid (rules + ML) final suggestion
"""

from .config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_DESCRIPTION,
    SUPPORTED_CROPS,
    FERTILIZER_NUTRIENT_PROFILE,
    ensure_directories_exist,
)

from .recommendation_engine import build_final_recommendation

__all__ = [
    "APP_TITLE",
    "APP_SUBTITLE",
    "APP_DESCRIPTION",
    "SUPPORTED_CROPS",
    "FERTILIZER_NUTRIENT_PROFILE",
    "ensure_directories_exist",
    "build_final_recommendation",
]
