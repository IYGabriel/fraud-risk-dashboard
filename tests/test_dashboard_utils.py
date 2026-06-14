import pandas as pd
import pytest

from services.dashboard_utils import (
    create_rule_counts,
    find_missing_dashboard_columns,
    format_list,
    normalise_columns,
    parse_rule_list,
)


def test_normalise_columns_removes_spaces() -> None:
    transactions = pd.DataFrame(
        {
            " Risk Score ": [20],
            "Risk Level": ["Low"],
            "Decision": ["Approve"],
            "Alert Priority": ["Low"],
            "Alert Status": ["Closed"],
        }
    )

    result = normalise_columns(
        transactions
    )

    assert "risk_score" in result.columns
    assert "risk_level" in result.columns
    assert "decision" in result.columns
    assert "alert_priority" in result.columns
    assert "alert_status" in result.columns


def test_find_missing_dashboard_columns() -> None:
    transactions = pd.DataFrame(
        {
            "transaction_id": ["TXN-1"],
            "risk_score": [50],
        }
    )

    missing_columns = (
        find_missing_dashboard_columns(
            transactions
        )
    )

    assert "decision" in missing_columns
    assert "risk_level" in missing_columns
    assert "alert_status" in missing_columns


def test_format_list_converts_list_to_text() -> None:
    result = format_list(
        [
            "new_device",
            "high_velocity",
        ]
    )

    assert result == (
        "new_device, high_velocity"
    )


def test_format_list_handles_none() -> None:
    assert format_list(None) == ""


def test_parse_rule_list_handles_list() -> None:
    result = parse_rule_list(
        [
            "new_device",
            "high_velocity",
        ]
    )

    assert result == [
        "new_device",
        "high_velocity",
    ]


def test_parse_rule_list_handles_string_list() -> None:
    result = parse_rule_list(
        "['new_device', 'high_velocity']"
    )

    assert result == [
        "new_device",
        "high_velocity",
    ]


def test_parse_rule_list_handles_comma_text() -> None:
    result = parse_rule_list(
        "new_device, high_velocity"
    )

    assert result == [
        "new_device",
        "high_velocity",
    ]


def test_create_rule_counts() -> None:
    transactions = pd.DataFrame(
        {
            "triggered_rules": [
                [
                    "new_device",
                    "high_velocity",
                ],
                [
                    "new_device",
                ],
            ]
        }
    )

    result = create_rule_counts(
        transactions
    )

    counts = dict(
        zip(
            result["rule"],
            result["count"],
        )
    )

    assert counts["new_device"] == 2
    assert counts["high_velocity"] == 1


def test_create_rule_counts_handles_no_rules() -> None:
    transactions = pd.DataFrame(
        {
            "triggered_rules": [
                [],
                [],
            ]
        }
    )

    result = create_rule_counts(
        transactions
    )

    assert result.empty


def test_create_rule_counts_rejects_missing_column() -> None:
    transactions = pd.DataFrame(
        {
            "risk_score": [20],
        }
    )

    with pytest.raises(
        ValueError,
        match="triggered_rules",
    ):
        create_rule_counts(
            transactions
        )