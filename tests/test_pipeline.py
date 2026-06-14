from pathlib import Path

import pandas as pd
import pytest

from services.pipeline import (
    run_fraud_pipeline,
    set_active_score,
)


SAMPLE_INPUT_PATH = Path(
    "data/raw/sample_transactions.csv"
)


def test_pipeline_returns_scored_transactions() -> None:
    result = run_fraud_pipeline(
        input_path=SAMPLE_INPUT_PATH,
        output_path=None,
    )

    expected_columns = {
        "risk_score",
        "risk_level",
        "triggered_rules",
        "risk_reasons",
        "decision",
        "alert_priority",
        "alert_status",
        "scoring_mode",
    }

    assert expected_columns.issubset(
        result.columns
    )

    assert len(result) > 0

    assert (
        result["scoring_mode"]
        == "rules"
    ).all()


def test_pipeline_scores_known_high_risk_transaction() -> None:
    result = run_fraud_pipeline(
        input_path=SAMPLE_INPUT_PATH,
        output_path=None,
    )

    high_risk_transactions = result[
        result["risk_level"] == "High"
    ]

    assert not high_risk_transactions.empty

    assert (
        high_risk_transactions[
            "decision"
        ]
        == "Block"
    ).all()


def test_pipeline_saves_output_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path
        / "scored_transactions.csv"
    )

    result = run_fraud_pipeline(
        input_path=SAMPLE_INPUT_PATH,
        output_path=output_path,
    )

    assert output_path.exists()

    saved_result = pd.read_csv(
        output_path
    )

    assert len(saved_result) == len(
        result
    )

    assert "decision" in saved_result.columns
    assert "scoring_mode" in saved_result.columns


def test_pipeline_supports_model_mode() -> None:
    result = run_fraud_pipeline(
        input_path=SAMPLE_INPUT_PATH,
        output_path=None,
        scoring_mode="model",
    )

    expected_columns = {
        "fraud_probability",
        "model_risk_level",
        "risk_score",
        "risk_level",
        "decision",
        "scoring_mode",
    }

    assert expected_columns.issubset(
        result.columns
    )

    assert (
        result["scoring_mode"]
        == "model"
    ).all()


def test_pipeline_supports_hybrid_mode() -> None:
    result = run_fraud_pipeline(
        input_path=SAMPLE_INPUT_PATH,
        output_path=None,
        scoring_mode="hybrid",
    )

    expected_columns = {
        "fraud_probability",
        "model_risk_level",
        "hybrid_score",
        "hybrid_risk_level",
        "risk_score",
        "risk_level",
        "decision",
        "scoring_mode",
    }

    assert expected_columns.issubset(
        result.columns
    )

    assert (
        result["scoring_mode"]
        == "hybrid"
    ).all()


def test_pipeline_rejects_invalid_scoring_mode() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported scoring mode",
    ):
        run_fraud_pipeline(
            input_path=SAMPLE_INPUT_PATH,
            output_path=None,
            scoring_mode="invalid",
        )


def test_set_active_score_for_model_mode() -> None:
    transactions = pd.DataFrame(
        {
            "risk_score": [20],
            "risk_level": ["Low"],
            "fraud_probability": [0.85],
            "model_risk_level": ["High"],
        }
    )

    result = set_active_score(
        transactions,
        scoring_mode="model",
    )

    assert (
        result.iloc[0]["risk_score"]
        == 85.0
    )

    assert (
        result.iloc[0]["risk_level"]
        == "High"
    )


def test_set_active_score_for_hybrid_mode() -> None:
    transactions = pd.DataFrame(
        {
            "risk_score": [20],
            "risk_level": ["Low"],
            "hybrid_score": [65.5],
            "hybrid_risk_level": ["High"],
        }
    )

    result = set_active_score(
        transactions,
        scoring_mode="hybrid",
    )

    assert (
        result.iloc[0]["risk_score"]
        == 65.5
    )

    assert (
        result.iloc[0]["risk_level"]
        == "High"
    )