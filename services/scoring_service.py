from __future__ import annotations

from typing import Literal, cast

import pandas as pd

from services.model_service import (
    predict_fraud_probability,
)
from services.risk_engine import apply_risk_rules


ScoringMode = Literal[
    "rules",
    "model",
    "hybrid",
]


def validate_scoring_mode(
    scoring_mode: str,
) -> ScoringMode:
    """
    Validate and return a supported scoring mode.
    """
    supported_modes = {
        "rules",
        "model",
        "hybrid",
    }

    normalised_mode = (
        str(scoring_mode)
        .strip()
        .lower()
    )

    if normalised_mode not in supported_modes:
        raise ValueError(
            "Unsupported scoring mode. "
            "Use 'rules', 'model', or 'hybrid'."
        )

    return cast(
        ScoringMode,
        normalised_mode,
    )


def add_hybrid_score(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine rule score and model probability.

    Rule score contributes 60%.
    Model probability contributes 40%.
    """
    required_columns = {
        "risk_score",
        "fraud_probability",
    }

    missing_columns = (
        required_columns
        - set(transactions.columns)
    )

    if missing_columns:
        raise ValueError(
            "Cannot calculate hybrid score. "
            f"Missing columns: {sorted(missing_columns)}"
        )

    scored = transactions.copy()

    rule_component = pd.to_numeric(
        scored["risk_score"],
        errors="coerce",
    ).clip(
        lower=0,
        upper=100,
    )

    model_component = (
        pd.to_numeric(
            scored["fraud_probability"],
            errors="coerce",
        )
        .clip(
            lower=0,
            upper=1,
        )
        * 100
    )

    if rule_component.isna().any():
        raise ValueError(
            "Rule scores must contain valid numeric values."
        )

    if model_component.isna().any():
        raise ValueError(
            "Model probabilities must contain "
            "valid numeric values."
        )

    scored["hybrid_score"] = (
        rule_component * 0.60
        + model_component * 0.40
    ).round(2)

    scored["hybrid_risk_level"] = scored[
        "hybrid_score"
    ].apply(
        lambda score: (
            "High"
            if score >= 60
            else "Medium"
            if score >= 30
            else "Low"
        )
    )

    return scored


def score_transactions(
    transactions: pd.DataFrame,
    scoring_mode: str = "rules",
) -> pd.DataFrame:
    """
    Score transactions using rules, model, or hybrid mode.
    """
    mode = validate_scoring_mode(
        scoring_mode
    )

    rule_scored = apply_risk_rules(
        transactions
    )

    if mode == "rules":
        result = rule_scored.copy()
        result["scoring_mode"] = "rules"
        return result

    model_scored = predict_fraud_probability(
        rule_scored
    )

    if mode == "model":
        result = model_scored.copy()
        result["scoring_mode"] = "model"
        return result

    hybrid_scored = add_hybrid_score(
        model_scored
    )

    hybrid_scored["scoring_mode"] = "hybrid"

    return hybrid_scored