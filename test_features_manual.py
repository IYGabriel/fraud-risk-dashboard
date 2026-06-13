from services.data_loader import load_transactions
from services.feature_engineering import add_features


def main() -> None:
    transactions = load_transactions(
        "data/raw/sample_transactions.csv"
    )

    featured = add_features(transactions)

    columns_to_show = [
        "transaction_id",
        "amount",
        "customer_average_amount",
        "transaction_hour",
        "is_night_transaction",
        "amount_vs_customer_average",
        "country_mismatch",
        "is_high_velocity",
        "is_new_account",
        "high_risk_transaction_type",
    ]

    print(featured[columns_to_show])


if __name__ == "__main__":
    main()