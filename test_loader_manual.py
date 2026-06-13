from services.data_loader import load_transactions


def main() -> None:
    transactions = load_transactions(
        "data/raw/sample_transactions.csv"
    )

    print("Dataset loaded successfully.")
    print(f"Rows: {len(transactions)}")
    print(f"Columns: {len(transactions.columns)}")
    print()
    print(transactions.head())


if __name__ == "__main__":
    main()