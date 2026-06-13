from __future__ import annotations

from pathlib import Path

import pandas as pd

from services.data_loader import load_transactions
from services.feature_engineering import add_features
from services.risk_engine import apply_risk_rules


DEFAULT_OUTPUT_PATH = Path(
    "data/processed/scored_transactions.csv"
)


def run_fraud_pipeline(
    input_path: str | Path,
    output_path: str | Path | None = DEFAULT_OUTPUT_PATH,
) -> pd.DataFrame:
    """
    Run the complete rule-based fraud-risk pipeline.

    Steps:
    1. Load and validate transaction data.
    2. Create fraud-risk features.
    3. Apply configurable fraud rules.
    4. Optionally save the scored transactions.
    """
    transactions = load_transactions(input_path)

    featured_transactions = add_features(transactions)

    scored_transactions = apply_risk_rules(
        featured_transactions
    )

    if output_path is not None:
        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        scored_transactions.to_csv(
            output,
            index=False,
        )

    return scored_transactions