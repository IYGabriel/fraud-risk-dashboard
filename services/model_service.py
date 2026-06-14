from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ModelPrediction:
    fraud_probability: float
    model_risk_level: str


def probability_to_risk_level(
    probability: float,
) -> str:
    """
    Convert a fraud probability into a risk level.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "Fraud probability must be between 0 and 1."
        )

    if probability >= 0.80:
        return "High"

    if probability >= 0.40:
        return "Medium"

    return "Low"


def predict_fraud_probability(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Placeholder machine-learning model interface.

    This function creates a model-compatible probability
    using the existing rule-based risk score until a trained
    model is added.
    """
    if "risk_score" not in transactions.columns:
        raise ValueError(
            "The DataFrame must contain 'risk_score' "
            "before model prediction."
        )

    predictions = transactions.copy()

    risk_scores = pd.to_numeric(
        predictions["risk_score"],
        errors="coerce",
    )

    if risk_scores.isna().any():
        raise ValueError(
            "Risk scores must contain valid numeric values."
        )

    predictions["fraud_probability"] = (
        risk_scores.clip(
            lower=0,
            upper=100,
        )
        / 100
    )

    predictions["model_risk_level"] = predictions[
        "fraud_probability"
    ].apply(
        probability_to_risk_level
    )

    return predictions