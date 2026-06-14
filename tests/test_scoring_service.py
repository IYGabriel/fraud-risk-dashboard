import pandas as pd
import pytest

from services.scoring_service import (
    add_hybrid_score,
    score_transactions,
    validate_scoring_mode,
)


def create_transaction() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "transaction_id": "TXN-1",
                "transaction_hour": 2,
                "is_night_transaction": True,
                "amount_vs_customer_average": 5.0,
                "country_mismatch": True,
                "is_high_velocity": True,
                "is_new_account": False,
                "is_new_device": True,
                "is_new_beneficiary": True,
                "high_risk_transaction_type": True,
            }
        ]
    )


def test_validate_scoring_mode() -> None:
    assert validate_scoring_mode(
        "RULES"
    ) == "rules"

    assert validate_scoring_mode(
        " model "
    ) == "model"


def test_invalid_scoring_mode_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported scoring mode",
    ):
        validate_scoring_mode(
            "unknown"
        )


def test_rule_scoring_mode() -> None:
    result = score_transactions(
        create_transaction(),
        scoring_mode="rules",
    )

    assert "risk_score" in result.columns
    assert result.iloc[0]["scoring_mode"] == "rules"


def test_model_scoring_mode() -> None:
    result = score_transactions(
        create_transaction(),
        scoring_mode="model",
    )

    assert "fraud_probability" in result.columns
    assert "model_risk_level" in result.columns
    assert result.iloc[0]["scoring_mode"] == "model"


def test_hybrid_scoring_mode() -> None:
    result = score_transactions(
        create_transaction(),
        scoring_mode="hybrid",
    )

    assert "hybrid_score" in result.columns
    assert "hybrid_risk_level" in result.columns
    assert result.iloc[0]["scoring_mode"] == "hybrid"


def test_add_hybrid_score() -> None:
    transactions = pd.DataFrame(
        {
            "risk_score": [80],
            "fraud_probability": [0.50],
        }
    )

    result = add_hybrid_score(
        transactions
    )

    assert result.iloc[0]["hybrid_score"] == 68.0
    assert (
        result.iloc[0]["hybrid_risk_level"]
        == "High"
    )