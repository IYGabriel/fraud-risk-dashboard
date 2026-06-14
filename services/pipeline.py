from __future__ import annotations

from pathlib import Path

import pandas as pd

from services.alert_engine import add_alert_decisions
from services.data_loader import load_transactions
from services.feature_engineering import add_features
from services.scoring_service import (
    score_transactions,
    validate_scoring_mode,
)


DEFAULT_OUTPUT_PATH = Path(
    "data/processed/scored_transactions.csv"
)


def set_active_score(
    transactions: pd.DataFrame,
    scoring_mode: str,
) -> pd.DataFrame:
    """
    Set the score and risk level used by the alert engine.

    Rules mode uses risk_score and risk_level.
    Model mode uses fraud_probability and model_risk_level.
    Hybrid mode uses hybrid_score and hybrid_risk_level.
    """
    mode = validate_scoring_mode(
        scoring_mode
    )

    result = transactions.copy()

    if mode == "model":
        result["risk_score"] = (
            result["fraud_probability"]
            * 100
        ).round(2)

        result["risk_level"] = result[
            "model_risk_level"
        ]

    elif mode == "hybrid":
        result["risk_score"] = result[
            "hybrid_score"
        ]

        result["risk_level"] = result[
            "hybrid_risk_level"
        ]

    return result


def run_fraud_pipeline(
    input_path: str | Path,
    output_path: str | Path | None = DEFAULT_OUTPUT_PATH,
    scoring_mode: str = "rules",
) -> pd.DataFrame:
    """
    Run the complete fraud-risk pipeline.

    Supported scoring modes:
    - rules
    - model
    - hybrid
    """
    transactions = load_transactions(
        input_path
    )

    featured_transactions = add_features(
        transactions
    )

    scored_transactions = score_transactions(
        featured_transactions,
        scoring_mode=scoring_mode,
    )

    active_scored_transactions = set_active_score(
        scored_transactions,
        scoring_mode=scoring_mode,
    )

    alerted_transactions = add_alert_decisions(
        active_scored_transactions
    )

    if output_path is not None:
        output = Path(
            output_path
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        alerted_transactions.to_csv(
            output,
            index=False,
        )

    return alerted_transactions