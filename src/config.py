from pathlib import Path


# PATH CONFIG


# Base project directory (…/crop_fertilizer_suggester)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXAMPLES_DATA_DIR = DATA_DIR / "examples"

# Models folder
MODELS_DIR = BASE_DIR / "models"

# App folder (for assets etc.)
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = APP_DIR / "assets"

# Default model paths
MODEL_FILE = MODELS_DIR / "trained_model.pkl"
SCALER_FILE = MODELS_DIR / "scaler.pkl"
ENCODER_FILE = MODELS_DIR / "encoder.pkl"


# DOMAIN CONSTANTS – AGRICULTURE + CHEMISTRY


# Expected soil input features (keep same order in preprocessing + model)
SOIL_FEATURES = [
    "pH",
    "organic_carbon",   # %
    "nitrogen",         # N kg/ha or similar
    "phosphorus",       # P kg/ha
    "potassium",        # K kg/ha
    "soil_type",        # categorical (e.g. clay, loam, sandy)
    "rainfall",         # mm
    "temperature",      # °C
    "ec",               # electrical conductivity (dS/m)
]

# Example crops supported by the system
SUPPORTED_CROPS = [
    "Rice",
    "Wheat",
    "Maize",
    "Sugarcane",
    "Cotton",
    "Pulses",
    "Vegetables",
    "Fruits",
]

# High-level fertilizer categories (for UI + explanation)
FERTILIZER_TYPES = [
    "Nitrogenous",
    "Phosphatic",
    "Potassic",
    "NPK_Complex",
    "Organic_Manure",
    "Biofertilizer",
]

# Mapping of some common fertilizers to their main nutrients
FERTILIZER_NUTRIENT_PROFILE = {
    "Urea": {"N": 46, "P": 0, "K": 0, "type": "Nitrogenous"},
    "Ammonium Sulphate": {"N": 21, "P": 0, "K": 0, "S": 24, "type": "Nitrogenous"},
    "DAP": {"N": 18, "P": 46, "K": 0, "type": "Phosphatic"},
    "SSP": {"N": 0, "P": 16, "K": 0, "S": 12, "type": "Phosphatic"},
    "MOP": {"N": 0, "P": 0, "K": 60, "type": "Potassic"},
    "NPK_17_17_17": {"N": 17, "P": 17, "K": 17, "type": "NPK_Complex"},
    "NPK_20_20_0": {"N": 20, "P": 20, "K": 0, "type": "NPK_Complex"},
    "FYM": {"N": 0.5, "P": 0.2, "K": 0.5, "type": "Organic_Manure"},
    "Vermicompost": {"N": 1.5, "P": 0.9, "K": 1.2, "type": "Organic_Manure"},
}

# Soil health index thresholds (you can tune during experiments)
SOIL_HEALTH_THRESHOLDS = {
    "excellent": 0.8,
    "good": 0.6,
    "moderate": 0.4,
    "poor": 0.0,
}

# pH interpretation bands
PH_BANDS = {
    "strongly_acidic": (0.0, 5.5),
    "moderately_acidic": (5.5, 6.5),
    "neutral": (6.5, 7.5),
    "slightly_alkaline": (7.5, 8.5),
    "strongly_alkaline": (8.5, 14.0),
}


# GENERAL APP SETTINGS


APP_TITLE = "Crop-Fertilizer Suggestion System"
APP_SUBTITLE = "Smart agriculture & chemistry of fertilizers"
APP_DESCRIPTION = (
    "An experiential learning tool that connects soil data, crop needs, and the "
    "chemistry of fertilizers to suggest safer and smarter fertilizer practices."
)

RANDOM_STATE = 42  # For reproducible ML results


def ensure_directories_exist() -> None:
    """
    Create essential directories if they don't exist yet.
    Call this once at app startup or before training the model.
    """
    for path in [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXAMPLES_DATA_DIR,
        MODELS_DIR,
        ASSETS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Quick sanity check when running this file directly
    print("Base directory:", BASE_DIR)
    ensure_directories_exist()
    print("All required directories are ready.")
