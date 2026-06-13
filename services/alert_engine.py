from __future__ import annotations

import pandas as pd


def determine_decision(
    risk_score: int,
    risk_level: str,
) -> str:
    """
    Convert a fraud risk result into an operational decision.
    """
    if risk_level == "High":
        return "Block"

    if risk_level == "Medium":
        return "Manual Review"

    return "Approve"


def determine_alert_priority(
    risk_score: int,
) -> str:
    """
    Assign an alert priority based on the numerical risk score.
    """
    if risk_score >= 80:
        return "Critical"

    if risk_score >= 60:
        return "High"

    if risk_score >= 30:
        return "Medium"

    return "Low"


def create_alert_status(
    decision: str,
) -> str:
    """
    Set the initial workflow status for the transaction.
    """
    if decision == "Approve":
        return "Closed"

    return "Open"


def add_alert_decisions(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add operational decisions and alert information
    to scored transactions.
    """
    required_columns = {
        "risk_score",
        "risk_level",
    }

    missing_columns = (
        required_columns - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required alert columns: "
            f"{sorted(missing_columns)}"
        )

    alerts = dataframe.copy()

    alerts["decision"] = alerts.apply(
        lambda row: determine_decision(
            risk_score=int(row["risk_score"]),
            risk_level=str(row["risk_level"]),
        ),
        axis=1,
    )

    alerts["alert_priority"] = alerts[
        "risk_score"
    ].apply(
        lambda score: determine_alert_priority(
            int(score)
        )
    )

    alerts["alert_status"] = alerts[
        "decision"
    ].apply(create_alert_status)

    return alerts