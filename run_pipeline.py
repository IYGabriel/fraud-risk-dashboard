from services.pipeline import run_fraud_pipeline


def main() -> None:
    scored_transactions = run_fraud_pipeline(
        input_path="data/raw/sample_transactions.csv",
        output_path=(
            "data/processed/scored_transactions.csv"
        ),
    )

    columns_to_show = [
        "transaction_id",
        "amount",
        "transaction_type",
        "risk_score",
        "risk_level",
        "triggered_rules",
    ]

    print(scored_transactions[columns_to_show])

    print(
        "\nScored dataset saved to: "
        "data/processed/scored_transactions.csv"
    )


if __name__ == "__main__":
    main()