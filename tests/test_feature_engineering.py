import pandas as pd

from services.feature_engineering import (
    add_features,
    calculate_amount_ratio,
)


def create_feature_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "transaction_id": "TXN-001",
                "timestamp": pd.Timestamp(
                    "2026-06-11T02:15:00Z"
                ),
                "amount": 7500,
                "customer_average_amount": 850,
                "country": "Ireland",
                "customer_usual_country": "Ireland",
                "transactions_last_1h": 6,
                "account_age_days": 12,
                "transaction_type": "international_transfer",
            },
            {
                "transaction_id": "TXN-002",
                "timestamp": pd.Timestamp(
                    "2026-06-11T14:30:00Z"
                ),
                "amount": 100,
                "customer_average_amount": 100,
                "country": "United Kingdom",
                "customer_usual_country": "Ireland",
                "transactions_last_1h": 1,
                "account_age_days": 365,
                "transaction_type": "card_payment",
            },
        ]
    )


def test_add_features_creates_expected_columns() -> None:
    dataframe = create_feature_dataframe()

    result = add_features(dataframe)

    expected_columns = {
        "transaction_hour",
        "is_night_transaction",
        "amount_vs_customer_average",
        "country_mismatch",
        "is_high_velocity",
        "is_new_account",
        "high_risk_transaction_type",
    }

    assert expected_columns.issubset(result.columns)


def test_high_risk_transaction_features() -> None:
    dataframe = create_feature_dataframe()

    result = add_features(dataframe)
    first_row = result.iloc[0]

    assert first_row["transaction_hour"] == 2
    assert bool(first_row["is_night_transaction"]) is True
    assert first_row["amount_vs_customer_average"] == 8.82
    assert bool(first_row["country_mismatch"]) is False
    assert bool(first_row["is_high_velocity"]) is True
    assert bool(first_row["is_new_account"]) is True
    assert bool(first_row["high_risk_transaction_type"]) is True


def test_low_risk_transaction_features() -> None:
    dataframe = create_feature_dataframe()

    result = add_features(dataframe)
    second_row = result.iloc[1]

    assert second_row["transaction_hour"] == 14
    assert bool(second_row["is_night_transaction"]) is False
    assert second_row["amount_vs_customer_average"] == 1.0
    assert bool(second_row["country_mismatch"]) is True
    assert bool(second_row["is_high_velocity"]) is False
    assert bool(second_row["is_new_account"]) is False
    assert bool(second_row["high_risk_transaction_type"]) is False


def test_zero_customer_average_does_not_crash() -> None:
    amount = pd.Series([500])
    customer_average = pd.Series([0])

    result = calculate_amount_ratio(
        amount,
        customer_average,
    )

    assert result.iloc[0] == 0