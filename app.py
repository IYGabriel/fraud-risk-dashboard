from __future__ import annotations

import ast
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from services.alert_engine import add_alert_decisions
from services.pipeline import run_fraud_pipeline


st.set_page_config(
    page_title="Fraud Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
)


def normalise_columns(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Standardise column names and ensure alert fields exist.
    """
    transactions = transactions.copy()

    transactions.columns = (
        transactions.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_alert_columns = {
        "decision",
        "alert_priority",
        "alert_status",
    }

    if not required_alert_columns.issubset(
        set(transactions.columns)
    ):
        transactions = add_alert_decisions(
            transactions
        )

    return transactions


def load_dashboard_data() -> pd.DataFrame:
    """
    Run the fraud pipeline using the sample dataset.
    """
    transactions = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=None,
    )

    return normalise_columns(
        transactions
    )


def load_uploaded_data(
    uploaded_file: Any,
) -> pd.DataFrame:
    """
    Save an uploaded CSV temporarily and run it
    through the complete fraud pipeline.
    """
    temporary_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".csv",
            delete=False,
        ) as temporary_file:
            temporary_file.write(
                uploaded_file.getbuffer()
            )

            temporary_path = temporary_file.name

        transactions = run_fraud_pipeline(
            input_path=temporary_path,
            output_path=None,
        )

        return normalise_columns(
            transactions
        )

    finally:
        if temporary_path is not None:
            Path(
                temporary_path
            ).unlink(
                missing_ok=True
            )


def format_list(
    value: object,
) -> str:
    """
    Convert lists into readable dashboard text.
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
    Convert triggered-rule values into a clean list.
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
    rules: list[str] = []

    for value in transactions[
        "triggered_rules"
    ]:
        rules.extend(
            parse_rule_list(
                value
            )
        )

    if not rules:
        return pd.DataFrame(
            columns=[
                "rule",
                "count",
            ]
        )

    return (
        pd.Series(rules)
        .value_counts()
        .rename_axis("rule")
        .reset_index(name="count")
    )


def main() -> None:
    st.title(
        "🛡️ Fraud Risk Dashboard"
    )

    st.caption(
        "Rule-based transaction monitoring, fraud scoring "
        "and analyst decision support."
    )

    st.sidebar.header(
        "Data Source"
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        help=(
            "Upload a CSV using the same columns as "
            "the sample transaction dataset."
        ),
    )

    try:
        if uploaded_file is not None:
            transactions = load_uploaded_data(
                uploaded_file
            )

            st.sidebar.success(
                f"Loaded: {uploaded_file.name}"
            )

        else:
            transactions = load_dashboard_data()

            st.sidebar.info(
                "Using the sample transaction dataset."
            )

    except Exception as error:
        st.error(
            f"Unable to process transaction data: {error}"
        )
        st.stop()

    required_columns = {
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

    missing_columns = (
        required_columns
        - set(transactions.columns)
    )

    if missing_columns:
        st.error(
            "The dashboard is missing required columns: "
            f"{sorted(missing_columns)}"
        )

        st.write(
            "Available columns:",
            transactions.columns.tolist(),
        )

        st.stop()

    total_transactions = len(
        transactions
    )

    high_risk_transactions = int(
        (
            transactions["risk_level"]
            == "High"
        ).sum()
    )

    blocked_transactions = int(
        (
            transactions["decision"]
            == "Block"
        ).sum()
    )

    review_transactions = int(
        (
            transactions["decision"]
            == "Manual Review"
        ).sum()
    )

    metric_1, metric_2, metric_3, metric_4 = (
        st.columns(4)
    )

    metric_1.metric(
        "Total Transactions",
        total_transactions,
    )

    metric_2.metric(
        "High Risk",
        high_risk_transactions,
    )

    metric_3.metric(
        "Blocked",
        blocked_transactions,
    )

    metric_4.metric(
        "Manual Review",
        review_transactions,
    )

    st.divider()

    st.subheader(
        "Filters"
    )

    filter_1, filter_2, filter_3 = (
        st.columns(3)
    )

    with filter_1:
        selected_risk_levels = st.multiselect(
            "Risk level",
            options=[
                "High",
                "Medium",
                "Low",
            ],
            default=[
                "High",
                "Medium",
                "Low",
            ],
        )

    with filter_2:
        selected_decisions = st.multiselect(
            "Decision",
            options=[
                "Block",
                "Manual Review",
                "Approve",
            ],
            default=[
                "Block",
                "Manual Review",
                "Approve",
            ],
        )

    with filter_3:
        maximum_risk_score = int(
            transactions[
                "risk_score"
            ].max()
        )

        minimum_score = st.slider(
            "Minimum risk score",
            min_value=0,
            max_value=max(
                100,
                maximum_risk_score,
            ),
            value=0,
            step=5,
        )

    filtered_transactions = transactions[
        transactions[
            "risk_level"
        ].isin(
            selected_risk_levels
        )
        & transactions[
            "decision"
        ].isin(
            selected_decisions
        )
        & (
            transactions[
                "risk_score"
            ]
            >= minimum_score
        )
    ].copy()

    st.divider()

    st.subheader(
        "Fraud Analytics"
    )

    if filtered_transactions.empty:
        st.info(
            "No transactions match the current filters."
        )

    else:
        chart_1, chart_2 = (
            st.columns(2)
        )

        risk_level_counts = (
            filtered_transactions[
                "risk_level"
            ]
            .value_counts()
            .reindex(
                [
                    "High",
                    "Medium",
                    "Low",
                ],
                fill_value=0,
            )
            .rename_axis(
                "risk_level"
            )
            .reset_index(
                name="transactions"
            )
        )

        with chart_1:
            st.write(
                "#### Risk-Level Distribution"
            )

            st.bar_chart(
                risk_level_counts,
                x="risk_level",
                y="transactions",
                width="stretch",
            )

        decision_counts = (
            filtered_transactions[
                "decision"
            ]
            .value_counts()
            .reindex(
                [
                    "Block",
                    "Manual Review",
                    "Approve",
                ],
                fill_value=0,
            )
            .rename_axis(
                "decision"
            )
            .reset_index(
                name="transactions"
            )
        )

        with chart_2:
            st.write(
                "#### Decision Distribution"
            )

            st.bar_chart(
                decision_counts,
                x="decision",
                y="transactions",
                width="stretch",
            )

        chart_3, chart_4 = (
            st.columns(2)
        )

        transaction_value_by_risk = (
            filtered_transactions
            .groupby(
                "risk_level",
                as_index=False,
            )["amount"]
            .sum()
            .rename(
                columns={
                    "amount": "transaction_value",
                }
            )
        )

        risk_order = pd.CategoricalDtype(
            categories=[
                "High",
                "Medium",
                "Low",
            ],
            ordered=True,
        )

        transaction_value_by_risk[
            "risk_level"
        ] = transaction_value_by_risk[
            "risk_level"
        ].astype(
            risk_order
        )

        transaction_value_by_risk = (
            transaction_value_by_risk
            .sort_values(
                "risk_level"
            )
        )

        with chart_3:
            st.write(
                "#### Transaction Value by Risk Level"
            )

            st.bar_chart(
                transaction_value_by_risk,
                x="risk_level",
                y="transaction_value",
                width="stretch",
            )

        rule_counts = create_rule_counts(
            filtered_transactions
        )

        with chart_4:
            st.write(
                "#### Most Frequently Triggered Rules"
            )

            if rule_counts.empty:
                st.info(
                    "No fraud rules were triggered "
                    "for the selected transactions."
                )

            else:
                st.bar_chart(
                    rule_counts.head(10),
                    x="rule",
                    y="count",
                    width="stretch",
                )

    st.divider()

    st.subheader(
        "Transaction Monitoring Queue"
    )

    display_transactions = (
        filtered_transactions.copy()
    )

    display_transactions[
        "triggered_rules"
    ] = display_transactions[
        "triggered_rules"
    ].apply(
        format_list
    )

    display_transactions[
        "risk_reasons"
    ] = display_transactions[
        "risk_reasons"
    ].apply(
        format_list
    )

    display_columns = [
        "transaction_id",
        "timestamp",
        "customer_id",
        "amount",
        "currency",
        "transaction_type",
        "country",
        "risk_score",
        "risk_level",
        "decision",
        "alert_priority",
        "alert_status",
        "triggered_rules",
    ]

    available_display_columns = [
        column
        for column in display_columns
        if column
        in display_transactions.columns
    ]

    st.dataframe(
        display_transactions[
            available_display_columns
        ],
        width="stretch",
        hide_index=True,
    )

    st.caption(
        f"Showing {len(filtered_transactions)} of "
        f"{total_transactions} transactions."
    )

    csv_data = (
        filtered_transactions
        .to_csv(
            index=False
        )
        .encode(
            "utf-8"
        )
    )

    st.download_button(
        label="Download Scored Results",
        data=csv_data,
        file_name=(
            "fraud_scored_transactions.csv"
        ),
        mime="text/csv",
    )

    st.divider()

    st.subheader(
        "Transaction Investigation"
    )

    transaction_options = (
        display_transactions[
            "transaction_id"
        ].tolist()
    )

    if not transaction_options:
        st.info(
            "No transactions match the selected filters."
        )
        return

    selected_transaction_id = st.selectbox(
        "Select a transaction",
        options=transaction_options,
    )

    selected_transaction = (
        display_transactions.loc[
            display_transactions[
                "transaction_id"
            ]
            == selected_transaction_id
        ].iloc[0]
    )

    detail_1, detail_2, detail_3 = (
        st.columns(3)
    )

    detail_1.metric(
        "Risk Score",
        int(
            selected_transaction[
                "risk_score"
            ]
        ),
    )

    detail_2.metric(
        "Risk Level",
        selected_transaction[
            "risk_level"
        ],
    )

    detail_3.metric(
        "Decision",
        selected_transaction[
            "decision"
        ],
    )

    st.write(
        "### Triggered Rules"
    )

    if selected_transaction[
        "triggered_rules"
    ]:
        st.write(
            selected_transaction[
                "triggered_rules"
            ]
        )

    else:
        st.write(
            "No fraud rules were triggered."
        )

    st.write(
        "### Risk Explanation"
    )

    if selected_transaction[
        "risk_reasons"
    ]:
        st.write(
            selected_transaction[
                "risk_reasons"
            ]
        )

    else:
        st.write(
            "No elevated fraud-risk indicators detected."
        )

    with st.expander(
        "View complete transaction data"
    ):
        transaction_details = (
            selected_transaction.to_dict()
        )

        transaction_details = {
            key: (
                value.isoformat()
                if hasattr(
                    value,
                    "isoformat",
                )
                else value
            )
            for key, value
            in transaction_details.items()
        }

        st.json(
            transaction_details
        )


if __name__ == "__main__":
    main()