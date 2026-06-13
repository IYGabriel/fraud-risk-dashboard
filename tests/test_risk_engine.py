import pandas as pd

from services.risk_engine import (
    apply_risk_rules,
    determine_risk_level,
    load_rules,
    score_transaction,
)


def create_high_risk_transaction() -> pd.Series:
    return pd.Series(
        {
            "is_night_transaction": True,
            "amount_vs_customer_average": 8.82,
            "country_mismatch": False,
            "is_high_velocity": True,
            "is_new_account": True,
            "high_risk_transaction_type": True,
            "is_new_device": True,
            "is_new_beneficiary": True,
        }
    )


def create_low_risk_transaction() -> pd.Series:
    return pd.Series(
        {
            "is_night_transaction": False,
            "amount_vs_customer_average": 1.0,
            "country_mismatch": False,
            "is_high_velocity": False,
            "is_new_account": False,
            "high_risk_transaction_type": False,
            "is_new_device": False,
            "is_new_beneficiary": False,
        }
    )


def test_rules_configuration_loads() -> None:
    configuration = load_rules()

    assert "rules" in configuration
    assert "risk_thresholds" in configuration
    assert configuration["risk_thresholds"]["high"] == 60


def test_high_risk_transaction_scores_correctly() -> None:
    configuration = load_rules()

    result = score_transaction(
        create_high_risk_transaction(),
        configuration,
    )

    assert result["risk_score"] == 85
    assert result["risk_level"] == "High"
    assert "unusual_amount" in result["triggered_rules"]
    assert "high_velocity" in result["triggered_rules"]


def test_low_risk_transaction_scores_correctly() -> None:
    configuration = load_rules()

    result = score_transaction(
        create_low_risk_transaction(),
        configuration,
    )

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["triggered_rules"] == []
    assert result["risk_reasons"] == []


def test_risk_level_thresholds() -> None:
    thresholds = {
        "medium": 30,
        "high": 60,
    }

    assert determine_risk_level(29, thresholds) == "Low"
    assert determine_risk_level(30, thresholds) == "Medium"
    assert determine_risk_level(59, thresholds) == "Medium"
    assert determine_risk_level(60, thresholds) == "High"


def test_rules_are_applied_to_dataframe() -> None:
    dataframe = pd.DataFrame(
        [
            create_high_risk_transaction(),
            create_low_risk_transaction(),
        ]
    )

    result = apply_risk_rules(dataframe)

    assert len(result) == 2
    assert result.iloc[0]["risk_score"] == 85
    assert result.iloc[0]["risk_level"] == "High"
    assert result.iloc[1]["risk_score"] == 0
    assert result.iloc[1]["risk_level"] == "Low"