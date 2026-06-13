from __future__ import annotations

import numpy as np
import pandas as pd


HIGH_RISK_TRANSACTION_TYPES = {
    "crypto",
    "cash_out",
    "international_transfer",
}


def add_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Convert cleaned transaction data into fraud-risk features.

    Parameters
    ----------
    dataframe:
        Cleaned transaction data from data_loader.py.

    Returns
    -------
    pd.DataFrame
        A copy of the original data with engineered features added.
    """
    featured = dataframe.copy()

    featured["transaction_hour"] = featured["timestamp"].dt.hour

    featured["is_night_transaction"] = (
        featured["transaction_hour"].between(0, 5)
    )

    featured["amount_vs_customer_average"] = calculate_amount_ratio(
        amount=featured["amount"],
        customer_average=featured["customer_average_amount"],
    )

    featured["country_mismatch"] = (
        featured["country"].str.strip().str.lower()
        != featured["customer_usual_country"].str.strip().str.lower()
    )

    featured["is_high_velocity"] = (
        featured["transactions_last_1h"] >= 5
    )

    featured["is_new_account"] = (
        featured["account_age_days"] <= 30
    )

    featured["high_risk_transaction_type"] = (
        featured["transaction_type"]
        .str.strip()
        .str.lower()
        .isin(HIGH_RISK_TRANSACTION_TYPES)
    )

    return featured


def calculate_amount_ratio(
    amount: pd.Series,
    customer_average: pd.Series,
) -> pd.Series:
    """
    Calculate how many times larger the transaction amount is
    than the customer's normal average amount.

    A zero historical average is replaced with NaN to avoid
    division-by-zero errors, then the result is filled with 0.
    """
    safe_average = customer_average.replace(0, np.nan)

    ratio = amount / safe_average

    return ratio.fillna(0).round(2)