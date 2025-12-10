import pandas as pd
from pathlib import Path

from .config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    EXAMPLES_DATA_DIR,
)



# INTERNAL CSV LOADER


def _load_csv(path: Path, description: str = "") -> pd.DataFrame:
    """
    Simple CSV loader with a helpful error message if the file is missing.

    Parameters
    ----------
    path : Path
        Full path to the CSV file.
    description : str
        Short text describing what this file is used for (shown in error).

    Returns
    -------
    pd.DataFrame
    """
    if not path.exists():
        msg = (
            f"CSV file not found: {path}\n"
            f"Description: {description}\n\n"
            f"Create this file at the above location and try again."
        )
        raise FileNotFoundError(msg)

    return pd.read_csv(path)



# RAW DATA LOADERS


def load_raw_soil_samples() -> pd.DataFrame:
    """
    Load raw soil samples data.

    Expected file:
        data/raw/soil_samples_raw.csv

    You can design columns like:
        soil_id, pH, organic_carbon, nitrogen, phosphorus, potassium,
        soil_type, rainfall, temperature, ec, region
    """
    path = RAW_DATA_DIR / "soil_samples_raw.csv"
    return _load_csv(
        path,
        description="Raw soil samples data (original unprocessed readings).",
    )


def load_raw_crop_requirements() -> pd.DataFrame:
    """
    Load raw crop nutrient requirement data.

    Expected file:
        data/raw/crop_requirements_raw.csv

    Example columns:
        crop, min_pH, max_pH, N_req, P_req, K_req, season, notes
    """
    path = RAW_DATA_DIR / "crop_requirements_raw.csv"
    return _load_csv(
        path,
        description="Raw crop nutrient requirements and preferred soil conditions.",
    )


def load_raw_fertilizer_properties() -> pd.DataFrame:
    """
    Load raw fertilizer properties database.

    Expected file:
        data/raw/fertilizer_properties_raw.csv

    Example columns:
        name, type, N_pct, P_pct, K_pct, S_pct, notes, safety_notes
    """
    path = RAW_DATA_DIR / "fertilizer_properties_raw.csv"
    return _load_csv(
        path,
        description="Raw fertilizer composition and chemistry information.",
    )


# PROCESSED DATA LOADERS


def load_processed_soil_data() -> pd.DataFrame:
    """
    Load processed soil dataset (cleaned + ready for ML / analysis).

    Expected file:
        data/processed/soil_processed.csv
    """
    path = PROCESSED_DATA_DIR / "soil_processed.csv"
    return _load_csv(
        path,
        description="Processed soil data (after cleaning / feature engineering).",
    )


def load_processed_crop_nutrient_needs() -> pd.DataFrame:
    """
    Load processed crop nutrient requirement dataset.

    Expected file:
        data/processed/crop_nutrient_needs.csv
    """
    path = PROCESSED_DATA_DIR / "crop_nutrient_needs.csv"
    return _load_csv(
        path,
        description="Processed crop nutrient needs dataset.",
    )


def load_processed_fertilizer_db() -> pd.DataFrame:
    """
    Load processed fertilizer database.

    Expected file:
        data/processed/fertilizer_db.csv
    """
    path = PROCESSED_DATA_DIR / "fertilizer_db.csv"
    return _load_csv(
        path,
        description="Processed fertilizer database with nutrient percentages.",
    )



# TRAINING DATASET LOADER (FOR ML MODEL)


def load_training_dataset() -> pd.DataFrame:
    """
    Load the final training dataset for the ML model.

    Expected file:
        data/processed/training_dataset.csv

    Suggested columns (you can design as you like):
        pH, organic_carbon, nitrogen, phosphorus, potassium,
        soil_type, rainfall, temperature, ec,
        crop, recommended_fertilizer

    You will use this in train_model.py to fit the classifier.
    """
    path = PROCESSED_DATA_DIR / "training_dataset.csv"
    return _load_csv(
        path,
        description=(
            "Final training dataset combining soil features, crop and "
            "target fertilizer label."
        ),
    )



# EXAMPLE INPUTS (FOR DEMO / STREAMLIT)


def load_demo_inputs() -> pd.DataFrame:
    """
    Load example inputs to quickly demo the app in Streamlit.

    Expected file:
        data/examples/demo_inputs.csv

    Example columns:
        pH, organic_carbon, nitrogen, phosphorus, potassium,
        soil_type, rainfall, temperature, ec, crop
    """
    path = EXAMPLES_DATA_DIR / "demo_inputs.csv"
    return _load_csv(
        path,
        description="Demo inputs for showcasing predictions in the UI.",
    )


if __name__ == "__main__":
    # Quick manual test: won't run in Streamlit, only if you run this file directly.
    try:
        df_train = load_training_dataset()
        print("Training dataset loaded. Shape:", df_train.shape)
    except FileNotFoundError as e:
        print("NOTE:", e)
