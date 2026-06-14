from pathlib import Path

import pandas as pd
import pytest

from services.upload_validator import (
    REQUIRED_UPLOAD_COLUMNS,
    normalise_column_names,
    validate_uploaded_csv,
)


def create_valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": ["TXN-1"],
            "customer_id": ["CUST-1"],
            "timestamp": ["2026-01-01 10:00:00"],
            "amount": [100.0],
            "currency": ["EUR"],
            "transaction_type": ["transfer"],
            "country": ["IE"],
            "device_id": ["DEVICE-1"],
            "beneficiary_id": ["BEN-1"],
            "is_new_device": [False],
            "is_new_beneficiary": [False],
            "transactions_last_1h": [1],
            "account_age_days": [365],
            "customer_average_amount": [80.0],
            "customer_usual_country": ["IE"],
            "is_fraud": [False],
        }
    )


def test_normalise_column_names() -> None:
    columns = pd.Index(
        [
            " Transaction ID ",
            "Risk Score",
        ]
    )

    result = normalise_column_names(
        columns
    )

    assert result == [
        "transaction_id",
        "risk_score",
    ]


def test_valid_uploaded_csv(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "valid.csv"

    create_valid_dataframe().to_csv(
        file_path,
        index=False,
    )

    result = validate_uploaded_csv(
        file_path
    )

    assert len(result) == 1
    assert set(
        REQUIRED_UPLOAD_COLUMNS
    ).issubset(
        result.columns
    )


def test_empty_file_is_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        validate_uploaded_csv(
            file_path
        )


def test_csv_without_rows_is_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "headers_only.csv"

    pd.DataFrame(
        columns=sorted(
            REQUIRED_UPLOAD_COLUMNS
        )
    ).to_csv(
        file_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="no transaction rows",
    ):
        validate_uploaded_csv(
            file_path
        )


def test_missing_columns_are_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "missing.csv"

    pd.DataFrame(
        {
            "transaction_id": ["TXN-1"],
            "amount": [100.0],
        }
    ).to_csv(
        file_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_uploaded_csv(
            file_path
        )


def test_duplicate_transaction_ids_are_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "duplicates.csv"

    transactions = pd.concat(
        [
            create_valid_dataframe(),
            create_valid_dataframe(),
        ],
        ignore_index=True,
    )

    transactions.to_csv(
        file_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate transaction IDs",
    ):
        validate_uploaded_csv(
            file_path
        )


def test_blank_transaction_id_is_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "blank_id.csv"

    transactions = create_valid_dataframe()
    transactions.loc[
        0,
        "transaction_id",
    ] = "   "

    transactions.to_csv(
        file_path,
        index=False,
    )

    with pytest.raises(
        ValueError,
        match="cannot be blank",
    ):
        validate_uploaded_csv(
            file_path
        )


def test_missing_file_is_rejected(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "missing_file.csv"

    with pytest.raises(
        ValueError,
        match="could not be found",
    ):
        validate_uploaded_csv(
            file_path
        )