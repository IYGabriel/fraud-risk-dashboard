from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_UPLOAD_COLUMNS = {
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
    "is_fraud",
}


def normalise_column_names(
    columns: pd.Index,
) -> list[str]:
    """
    Convert uploaded column names into the format
    expected by the fraud pipeline.
    """
    return [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        for column in columns
    ]


def validate_uploaded_csv(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Read and validate an uploaded transaction CSV.

    Raises ValueError when the file is empty, malformed,
    missing required columns, or contains invalid IDs.
    """
    path = Path(file_path)

    if not path.exists():
        raise ValueError(
            "The uploaded file could not be found."
        )

    if path.stat().st_size == 0:
        raise ValueError(
            "The uploaded CSV is empty."
        )

    try:
        transactions = pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(
            "The uploaded CSV does not contain any data."
        ) from error
    except pd.errors.ParserError as error:
        raise ValueError(
            "The uploaded file is not a valid CSV."
        ) from error
    except UnicodeDecodeError as error:
        raise ValueError(
            "The uploaded CSV must use UTF-8 encoding."
        ) from error

    if transactions.empty:
        raise ValueError(
            "The uploaded CSV contains no transaction rows."
        )

    transactions.columns = normalise_column_names(
        transactions.columns
    )

    missing_columns = (
        REQUIRED_UPLOAD_COLUMNS
        - set(transactions.columns)
    )

    if missing_columns:
        raise ValueError(
            "The uploaded CSV is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if transactions["transaction_id"].isna().any():
        raise ValueError(
            "Transaction IDs cannot be empty."
        )

    transaction_ids = (
        transactions["transaction_id"]
        .astype(str)
        .str.strip()
    )

    if transaction_ids.eq("").any():
        raise ValueError(
            "Transaction IDs cannot be blank."
        )

    if transaction_ids.duplicated().any():
        duplicate_ids = (
            transaction_ids[
                transaction_ids.duplicated(
                    keep=False
                )
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            "Duplicate transaction IDs found: "
            f"{duplicate_ids}"
        )

    return transactions