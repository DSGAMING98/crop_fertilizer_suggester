from typing import Tuple, Dict, Any

import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import joblib

from .config import SOIL_FEATURES, SCALER_FILE



# FEATURE CONFIG


# We take all soil features + crop name as inputs to the model
INPUT_FEATURES = SOIL_FEATURES + ["crop"]

# Separate numeric vs categorical for preprocessing
NUMERIC_FEATURES = [
    "pH",
    "organic_carbon",
    "nitrogen",
    "phosphorus",
    "potassium",
    "rainfall",
    "temperature",
    "ec",
]

CATEGORICAL_FEATURES = [
    "soil_type",
    "crop",
]

TARGET_COLUMN = "recommended_fertilizer"



# SPLIT FEATURES + TARGET


def split_features_target(
    df: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split a dataframe into X (features) and y (target).

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe that contains both features and target.
    target_col : str
        Name of the target column (fertilizer label).

    Returns
    -------
    X : pd.DataFrame
        Feature dataframe containing soil + crop inputs.
    y : pd.Series
        Target series (fertilizer labels).
    """
    missing_cols = [col for col in INPUT_FEATURES if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required feature columns in training dataframe: {missing_cols}"
        )

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe.")

    X = df[INPUT_FEATURES].copy()
    y = df[target_col].astype(str)

    return X, y



# PREPROCESSOR (SCALER + ENCODER)


def build_preprocessor() -> ColumnTransformer:
    """
    Build a ColumnTransformer that:
      - Scales numeric features
      - One-hot encodes categorical features

    Returns
    -------
    preprocessor : ColumnTransformer
    """
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    return preprocessor


def fit_preprocessor(
    X: pd.DataFrame,
) -> ColumnTransformer:
    """
    Fit the preprocessor on the training features.

    Parameters
    ----------
    X : pd.DataFrame
        Feature dataframe with INPUT_FEATURES.

    Returns
    -------
    preprocessor : ColumnTransformer
        Fitted preprocessor.
    """
    missing_cols = [col for col in INPUT_FEATURES if col not in X.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required feature columns in X: {missing_cols}"
        )

    preprocessor = build_preprocessor()
    preprocessor.fit(X)

    return preprocessor


def transform_features(
    preprocessor: ColumnTransformer,
    X: pd.DataFrame,
):
    """
    Apply a fitted preprocessor to feature dataframe.

    Parameters
    ----------
    preprocessor : ColumnTransformer
        Fitted preprocessor (from fit_preprocessor).
    X : pd.DataFrame
        Feature dataframe.

    Returns
    -------
    X_transformed : np.ndarray
        Numpy array of transformed features.
    """
    missing_cols = [col for col in INPUT_FEATURES if col not in X.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required feature columns in X: {missing_cols}"
        )

    return preprocessor.transform(X)



# SAVE / LOAD PREPROCESSOR


def save_preprocessor(
    preprocessor: ColumnTransformer,
    path=SCALER_FILE,
) -> None:
    """
    Save the fitted preprocessor to disk.

    NOTE:
        We store the entire ColumnTransformer object in SCALER_FILE
        (name comes from config but it contains scaler + encoder).
    """
    joblib.dump(preprocessor, path)


def load_preprocessor(path=SCALER_FILE) -> ColumnTransformer:
    """
    Load a previously saved preprocessor from disk.
    """
    return joblib.load(path)



# SINGLE-ROW PREP (FOR STREAMLIT INPUTS)


def build_input_dataframe_from_dict(
    input_data: Dict[str, Any],
) -> pd.DataFrame:
    """
    Convert a simple dict into a one-row dataframe with correct column order.

    Parameters
    ----------
    input_data : dict
        Keys must include all INPUT_FEATURES.
        Example:
            {
                "pH": 6.7,
                "organic_carbon": 0.8,
                "nitrogen": 120,
                "phosphorus": 45,
                "potassium": 140,
                "soil_type": "Loam",
                "rainfall": 800,
                "temperature": 28,
                "ec": 0.7,
                "crop": "Rice",
            }

    Returns
    -------
    df : pd.DataFrame
        One-row dataframe ready for transform_features().
    """
    missing_keys = [k for k in INPUT_FEATURES if k not in input_data]
    if missing_keys:
        raise ValueError(
            f"Missing required keys in input_data: {missing_keys}"
        )

    # Ensure correct column order
    data_ordered = {col: input_data[col] for col in INPUT_FEATURES}
    df = pd.DataFrame([data_ordered])

    return df


if __name__ == "__main__":
    # Tiny self-check when running directly
    dummy = {
        "pH": 6.5,
        "organic_carbon": 0.8,
        "nitrogen": 120,
        "phosphorus": 45,
        "potassium": 140,
        "soil_type": "Loam",
        "rainfall": 800,
        "temperature": 28,
        "ec": 0.7,
        "crop": "Rice",
    }
    df_input = build_input_dataframe_from_dict(dummy)
    print("Input DF:\n", df_input)

    pre = fit_preprocessor(df_input)
    save_preprocessor(pre)
    print("Preprocessor saved at:", SCALER_FILE)
