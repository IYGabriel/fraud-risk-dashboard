from pathlib import Path

from services.pipeline import run_fraud_pipeline


def test_pipeline_returns_scored_transactions() -> None:
    result = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=None,
    )

    assert len(result) == 8
    assert "risk_score" in result.columns
    assert "risk_level" in result.columns
    assert "triggered_rules" in result.columns
    assert "risk_reasons" in result.columns


def test_pipeline_scores_known_high_risk_transaction() -> None:
    result = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=None,
    )

    transaction = result.loc[
        result["transaction_id"] == "TXN-10001"
    ].iloc[0]

    assert transaction["risk_score"] == 85
    assert transaction["risk_level"] == "High"
    assert "unusual_amount" in transaction["triggered_rules"]


def test_pipeline_saves_output_file(tmp_path: Path) -> None:
    output_path = tmp_path / "scored_transactions.csv"

    result = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=output_path,
    )

    assert output_path.exists()
    assert len(result) == 8