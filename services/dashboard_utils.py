from __future__ import annotations

import ast

import pandas as pd

from services.alert_engine import add_alert_decisions


REQUIRED_DASHBOARD_COLUMNS = {
    "transaction_id",
    "amount",
    "risk_score",
    "risk_level",
    "decision",
    "alert_priority",
    "alert_status",
    "triggered_rules",
    "risk_reasons",
}


def normalise_columns(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardise DataFrame column names and ensure that
    operational alert columns are present.
    """
    normalised = transactions.copy()

    normalised.columns = (
        normalised.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    alert_columns = {
        "decision",
        "alert_priority",
        "alert_status",
    }

    if not alert_columns.issubset(
        set(normalised.columns)
    ):
        normalised = add_alert_decisions(
            normalised
        )

    return normalised


def find_missing_dashboard_columns(
    transactions: pd.DataFrame,
) -> set[str]:
    """
    Return dashboard columns that are missing from
    the supplied DataFrame.
    """
    return (
        REQUIRED_DASHBOARD_COLUMNS
        - set(transactions.columns)
    )


def format_list(
    value: object,
) -> str:
    """
    Convert list-like values into readable text.
    """
    if isinstance(value, list):
        return ", ".join(
            str(item)
            for item in value
        )

    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value)


def parse_rule_list(
    value: object,
) -> list[str]:
    """
    Convert a triggered-rules value into a clean list.
    """
    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if value is None:
        return []

    try:
        if pd.isna(value):
            return []
    except (TypeError, ValueError):
        pass

    value_text = str(value).strip()

    if not value_text:
        return []

    try:
        parsed_value = ast.literal_eval(
            value_text
        )

        if isinstance(parsed_value, list):
            return [
                str(item).strip()
                for item in parsed_value
                if str(item).strip()
            ]

    except (ValueError, SyntaxError):
        pass

    return [
        item.strip()
        for item in value_text.split(",")
        if item.strip()
    ]


def create_rule_counts(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count how often each fraud rule was triggered.
    """
    if "triggered_rules" not in transactions.columns:
        raise ValueError(
            "The DataFrame does not contain "
            "'triggered_rules'."
        )

    rules: list[str] = []

    for value in transactions["triggered_rules"]:
        rules.extend(
            parse_rule_list(value)
        )

    if not rules:
        return pd.DataFrame(
            columns=[
                "rule",
                "count",
            ]
        )

    return (
        pd.Series(rules, dtype="object")
        .value_counts()
        .rename_axis("rule")
        .reset_index(name="count")
    )