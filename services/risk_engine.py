from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_RULES_PATH = Path("config/fraud_rules.yaml")


def load_rules(
    rules_path: str | Path = DEFAULT_RULES_PATH,
) -> dict[str, Any]:
    """
    Load fraud-rule weights and thresholds from a YAML file.
    """
    path = Path(rules_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Fraud rules file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        configuration = yaml.safe_load(file)

    if not configuration:
        raise ValueError("Fraud rules configuration is empty.")

    if "rules" not in configuration:
        raise ValueError(
            "Fraud rules configuration must contain a 'rules' section."
        )

    if "risk_thresholds" not in configuration:
        raise ValueError(
            "Fraud rules configuration must contain "
            "a 'risk_thresholds' section."
        )

    return configuration


def score_transaction(
    transaction: pd.Series,
    configuration: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate the fraud-risk score for one transaction.
    """
    rules = configuration["rules"]

    score = 0
    triggered_rules: list[str] = []
    risk_reasons: list[str] = []

    def apply_boolean_rule(
        rule_name: str,
        condition: bool,
    ) -> None:
        nonlocal score

        if condition:
            rule = rules[rule_name]
            score += int(rule["weight"])
            triggered_rules.append(rule_name)
            risk_reasons.append(rule["reason"])

    apply_boolean_rule(
        "night_transaction",
        bool(transaction["is_night_transaction"]),
    )

    unusual_amount_rule = rules["unusual_amount"]

    if (
        float(transaction["amount_vs_customer_average"])
        >= float(unusual_amount_rule["threshold"])
    ):
        score += int(unusual_amount_rule["weight"])
        triggered_rules.append("unusual_amount")
        risk_reasons.append(unusual_amount_rule["reason"])

    apply_boolean_rule(
        "country_mismatch",
        bool(transaction["country_mismatch"]),
    )

    apply_boolean_rule(
        "high_velocity",
        bool(transaction["is_high_velocity"]),
    )

    apply_boolean_rule(
        "new_account",
        bool(transaction["is_new_account"]),
    )

    apply_boolean_rule(
        "high_risk_transaction_type",
        bool(transaction["high_risk_transaction_type"]),
    )

    apply_boolean_rule(
        "new_device",
        bool(transaction["is_new_device"]),
    )

    apply_boolean_rule(
        "new_beneficiary",
        bool(transaction["is_new_beneficiary"]),
    )

    score = min(score, 100)

    risk_level = determine_risk_level(
        score=score,
        thresholds=configuration["risk_thresholds"],
    )

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "triggered_rules": triggered_rules,
        "risk_reasons": risk_reasons,
    }


def determine_risk_level(
    score: int,
    thresholds: dict[str, int],
) -> str:
    """
    Convert a numerical score into Low, Medium, or High risk.
    """
    if score >= int(thresholds["high"]):
        return "High"

    if score >= int(thresholds["medium"]):
        return "Medium"

    return "Low"


def apply_risk_rules(
    dataframe: pd.DataFrame,
    rules_path: str | Path = DEFAULT_RULES_PATH,
) -> pd.DataFrame:
    """
    Apply the fraud rules to every transaction in a DataFrame.
    """
    configuration = load_rules(rules_path)

    scored = dataframe.copy()

    results = scored.apply(
        lambda row: score_transaction(
            transaction=row,
            configuration=configuration,
        ),
        axis=1,
    )

    scored["risk_score"] = results.apply(
        lambda result: result["risk_score"]
    )

    scored["risk_level"] = results.apply(
        lambda result: result["risk_level"]
    )

    scored["triggered_rules"] = results.apply(
        lambda result: result["triggered_rules"]
    )

    scored["risk_reasons"] = results.apply(
        lambda result: result["risk_reasons"]
    )

    return scored