import pandas as pd
import pytest

from services.model_service import (
    predict_fraud_probability,
    probability_to_risk_level,
)


def test_probability_to_risk_level() -> None:
    assert probability_to_risk_level(0.20) == "Low"
    assert probability_to_risk_level(0.50) == "Medium"
    assert probability_to_risk_level(0.90) == "High"


def test_probability_rejects_invalid_value() -> None:
    with pytest.raises(
        ValueError,
        match="between 0 and 1",
    ):
        probability_to_risk_level(1.20)


def test_predict_fraud_probability() -> None:
    transactions = pd.DataFrame(
        {
            "risk_score": [
                10,
                50,
                90,
            ]
        }
    )

    result = predict_fraud_probability(
        transactions
    )

    assert result[
        "fraud_probability"
    ].tolist() == [
        0.10,
        0.50,
        0.90,
    ]

    assert result[
        "model_risk_level"
    ].tolist() == [
        "Low",
        "Medium",
        "High",
    ]


def test_prediction_requires_risk_score() -> None:
    transactions = pd.DataFrame(
        {
            "amount": [100.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="risk_score",
    ):
        predict_fraud_probability(
            transactions
        )