from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, ValidationError


class TransactionRecord(BaseModel):
    transaction_id: str
    customer_id: str
    timestamp: datetime
    amount: float = Field(ge=0)
    currency: str
    transaction_type: str
    country: str
    device_id: str
    beneficiary_id: str
    is_new_device: bool
    is_new_beneficiary: bool
    transactions_last_1h: int = Field(ge=0)
    account_age_days: int = Field(ge=0)
    customer_average_amount: float = Field(ge=0)
    customer_usual_country: str
    is_fraud: int | None = Field(default=None, ge=0, le=1)


REQUIRED_COLUMNS = {
    "transaction_id",
    "customer_id",
    "timestamp",
    "amount",
    "currency",
    "transaction_type",
    "country",
    "device_id",
    "beneficiary_id",
    "is_new_device",
    "is_new_beneficiary",
    "transactions_last_1h",
    "account_age_days",
    "customer_average_amount",
    "customer_usual_country",
}


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported in V1.")

    dataframe = pd.read_csv(file_path)

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    return clean_transactions(dataframe)


def clean_transactions(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned = dataframe.copy()

    cleaned["timestamp"] = pd.to_datetime(
        cleaned["timestamp"],
        errors="coerce",
        utc=True,
    )

    numeric_columns = [
        "amount",
        "transactions_last_1h",
        "account_age_days",
        "customer_average_amount",
    ]

    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce",
        )

    cleaned["is_new_device"] = convert_to_boolean(
        cleaned["is_new_device"]
    )

    cleaned["is_new_beneficiary"] = convert_to_boolean(
        cleaned["is_new_beneficiary"]
    )

    invalid_rows = cleaned[
        cleaned["timestamp"].isna()
        | cleaned["amount"].isna()
        | cleaned["transactions_last_1h"].isna()
        | cleaned["account_age_days"].isna()
        | cleaned["customer_average_amount"].isna()
    ]

    if not invalid_rows.empty:
        raise ValueError(
            f"{len(invalid_rows)} rows contain invalid dates or numeric values."
        )

    validate_records(cleaned)

    return cleaned


def convert_to_boolean(series: pd.Series) -> pd.Series:
    boolean_map = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }

    converted = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(boolean_map)
    )

    if converted.isna().any():
        raise ValueError(
            "Boolean columns must contain true/false, yes/no or 1/0."
        )

    return converted


def validate_records(dataframe: pd.DataFrame) -> None:
    errors: list[str] = []

    for row_number, row in dataframe.iterrows():
        try:
            TransactionRecord(**row.to_dict())
        except ValidationError as error:
            errors.append(
                f"Row {row_number}: {error.errors()}"
            )

    if errors:
        preview = "\n".join(errors[:5])
        raise ValueError(
            f"Transaction validation failed:\n{preview}"
        )