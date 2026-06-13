import pandas as pd
import pytest

from services.data_loader import clean_transactions


def create_valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "transaction_id": "TXN-001",
                "customer_id": "CUST-001",
                "timestamp": "2026-06-11T10:00:00Z",
                "amount": 500,
                "currency": "EUR",
                "transaction_type": "bank_transfer",
                "country": "Ireland",
                "device_id": "DEV-001",
                "beneficiary_id": "BEN-001",
                "is_new_device": False,
                "is_new_beneficiary": True,
                "transactions_last_1h": 2,
                "account_age_days": 100,
                "customer_average_amount": 250,
                "customer_usual_country": "Ireland",
                "is_fraud": 0,
            }
        ]
    )


def test_valid_transaction_is_cleaned() -> None:
    dataframe = create_valid_dataframe()

    result = clean_transactions(dataframe)

    assert len(result) == 1
    assert result.iloc[0]["amount"] == 500
    assert result.iloc[0]["is_new_beneficiary"]


def test_negative_amount_is_rejected() -> None:
    dataframe = create_valid_dataframe()
    dataframe.loc[0, "amount"] = -100

    with pytest.raises(ValueError):
        clean_transactions(dataframe)


def test_invalid_timestamp_is_rejected() -> None:
    dataframe = create_valid_dataframe()
    dataframe.loc[0, "timestamp"] = "not-a-date"

    with pytest.raises(ValueError):
        clean_transactions(dataframe)


def test_invalid_boolean_is_rejected() -> None:
    dataframe = create_valid_dataframe()

    dataframe["is_new_device"] = dataframe["is_new_device"].astype(object)
    dataframe.loc[0, "is_new_device"] = "sometimes"

    with pytest.raises(ValueError):
        clean_transactions(dataframe)