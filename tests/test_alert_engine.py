import pandas as pd
import pytest

from services.alert_engine import (
    add_alert_decisions,
    create_alert_status,
    determine_alert_priority,
    determine_decision,
)


def test_low_risk_transaction_is_approved() -> None:
    result = determine_decision(
        risk_score=10,
        risk_level="Low",
    )

    assert result == "Approve"


def test_medium_risk_transaction_requires_review() -> None:
    result = determine_decision(
        risk_score=45,
        risk_level="Medium",
    )

    assert result == "Manual Review"


def test_high_risk_transaction_is_blocked() -> None:
    result = determine_decision(
        risk_score=85,
        risk_level="High",
    )

    assert result == "Block"


def test_alert_priority_thresholds() -> None:
    assert determine_alert_priority(10) == "Low"
    assert determine_alert_priority(30) == "Medium"
    assert determine_alert_priority(60) == "High"
    assert determine_alert_priority(80) == "Critical"


def test_alert_status() -> None:
    assert create_alert_status("Approve") == "Closed"
    assert create_alert_status("Manual Review") == "Open"
    assert create_alert_status("Block") == "Open"


def test_alert_decisions_are_added_to_dataframe() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "transaction_id": "TXN-001",
                "risk_score": 85,
                "risk_level": "High",
            },
            {
                "transaction_id": "TXN-002",
                "risk_score": 0,
                "risk_level": "Low",
            },
        ]
    )

    result = add_alert_decisions(dataframe)

    assert result.iloc[0]["decision"] == "Block"
    assert (
        result.iloc[0]["alert_priority"]
        == "Critical"
    )
    assert result.iloc[0]["alert_status"] == "Open"

    assert result.iloc[1]["decision"] == "Approve"
    assert result.iloc[1]["alert_priority"] == "Low"
    assert result.iloc[1]["alert_status"] == "Closed"


def test_missing_risk_columns_are_rejected() -> None:
    dataframe = pd.DataFrame(
        [{"transaction_id": "TXN-001"}]
    )

    with pytest.raises(ValueError):
        add_alert_decisions(dataframe)