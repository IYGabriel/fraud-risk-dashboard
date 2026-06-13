from __future__ import annotations

import pandas as pd
import streamlit as st

from services.alert_engine import add_alert_decisions
from services.pipeline import run_fraud_pipeline


st.set_page_config(
    page_title="Fraud Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
)


def load_dashboard_data() -> pd.DataFrame:
    """
    Run the fraud pipeline and return the completed dataset.
    """
    transactions = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=None,
    )

    transactions.columns = (
        transactions.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Safety fallback in case the pipeline returns only risk scores.
    if "decision" not in transactions.columns:
        transactions = add_alert_decisions(
            transactions
        )

    return transactions


def format_list(value: object) -> str:
    """
    Convert lists into readable text for the dashboard.
    """
    if isinstance(value, list):
        return ", ".join(value)

    return str(value)


def main() -> None:
    st.title("🛡️ Fraud Risk Dashboard")

    st.caption(
        "Rule-based transaction monitoring, fraud scoring "
        "and analyst decision support."
    )

    try:
        transactions = load_dashboard_data()
    except Exception as error:
        st.error(
            f"Unable to load transaction data: {error}"
        )
        st.stop()

    required_columns = {
        "risk_score",
        "risk_level",
        "decision",
        "alert_priority",
        "alert_status",
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

    total_transactions = len(transactions)

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
    st.subheader("Transaction Monitoring Queue")

    filter_1, filter_2, filter_3 = st.columns(3)

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
        minimum_score = st.slider(
            "Minimum risk score",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )

    filtered_transactions = transactions[
        transactions["risk_level"].isin(
            selected_risk_levels
        )
        & transactions["decision"].isin(
            selected_decisions
        )
        & (
            transactions["risk_score"]
            >= minimum_score
        )
    ].copy()

    filtered_transactions[
        "triggered_rules"
    ] = filtered_transactions[
        "triggered_rules"
    ].apply(format_list)

    filtered_transactions[
        "risk_reasons"
    ] = filtered_transactions[
        "risk_reasons"
    ].apply(format_list)

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

    st.dataframe(
        filtered_transactions[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Showing {len(filtered_transactions)} of "
        f"{total_transactions} transactions."
    )

    st.divider()
    st.subheader("Transaction Investigation")

    transaction_options = (
        filtered_transactions[
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
        filtered_transactions.loc[
            filtered_transactions[
                "transaction_id"
            ]
            == selected_transaction_id
        ].iloc[0]
    )

    detail_1, detail_2, detail_3 = st.columns(3)

    detail_1.metric(
        "Risk Score",
        int(selected_transaction["risk_score"]),
    )

    detail_2.metric(
        "Risk Level",
        selected_transaction["risk_level"],
    )

    detail_3.metric(
        "Decision",
        selected_transaction["decision"],
    )

    st.write("### Triggered Rules")

    if selected_transaction["triggered_rules"]:
        st.write(
            selected_transaction["triggered_rules"]
        )
    else:
        st.write(
            "No fraud rules were triggered."
        )

    st.write("### Risk Explanation")

    if selected_transaction["risk_reasons"]:
        st.write(
            selected_transaction["risk_reasons"]
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
                if hasattr(value, "isoformat")
                else value
            )
            for key, value
            in transaction_details.items()
        }

        st.json(transaction_details)


if __name__ == "__main__":
    main()