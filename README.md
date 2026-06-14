# Fraud Risk Dashboard

A modular fraud-risk monitoring application built with Python, pandas, Streamlit, YAML configuration, and automated testing.

It processes transaction data, engineers behavioural risk features, applies configurable fraud rules, scores each transaction, and surfaces everything through an interactive analyst dashboard.

---

## What it does

- Accepts a CSV upload or uses a built-in demo dataset
- Validates uploaded files and shows friendly errors instead of crashing
- Engineers behavioural features from raw transaction data
- Scores transactions using configurable YAML fraud rules
- Supports three scoring modes: **Rules**, **Model**, and **Hybrid**
- Classifies each transaction as Low, Medium, or High risk
- Issues Approve, Manual Review, or Block decisions
- Assigns alert priority and open/closed status
- Renders an analytics dashboard with charts and a monitoring queue
- Lets analysts drill into individual transactions and see which rules fired
- Exports scored results as a downloadable CSV

---

## Scoring modes

### Rules
The default mode. Fraud rules are defined in `config/fraud_rules.yaml` — transparent, auditable, and easy to adjust without touching any code.

### Model
Returns a fraud probability, a model-derived risk level, and a model-based score. The current implementation is a placeholder that converts the rule score into a probability. It's designed to be swapped out for a trained classifier when one is ready.

### Hybrid
Blends 60% rule-based score with 40% model score. The architecture is ready for a real model — the weighting is already wired in.

---

## Risk decisions

| Risk level | Decision      |
|------------|---------------|
| Low        | Approve       |
| Medium     | Manual Review |
| High       | Block         |

## Alert priorities

| Risk score | Priority |
|------------|----------|
| 80–100     | Critical |
| 60–79      | High     |
| 30–59      | Medium   |
| 0–29       | Low      |

Approved transactions are automatically closed. Everything else stays open for analyst action.

---

## Dashboard

The Streamlit dashboard gives you:

- transaction volume, high-risk count, blocked count, and manual-review count at a glance
- filters by risk level, decision, and minimum score
- risk-level and decision distribution charts
- transaction value broken down by risk level
- a ranked view of the most frequently triggered fraud rules
- a transaction investigation panel with triggered-rule explanations
- a one-click CSV export of scored results

---

## Project structure

```
fraud-risk-dashboard/
├── app.py
├── config/
│   └── fraud_rules.yaml
├── data/
│   ├── raw/
│   │   └── sample_transactions.csv
│   └── processed/
├── services/
│   ├── __init__.py
│   ├── alert_engine.py
│   ├── dashboard_utils.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── model_service.py
│   ├── pipeline.py
│   ├── risk_engine.py
│   ├── scoring_service.py
│   └── upload_validator.py
├── tests/
│   ├── __init__.py
│   ├── test_alert_engine.py
│   ├── test_dashboard_utils.py
│   ├── test_data_loader.py
│   ├── test_feature_engineering.py
│   ├── test_model_service.py
│   ├── test_pipeline.py
│   ├── test_risk_engine.py
│   ├── test_scoring_service.py
│   └── test_upload_validator.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## How data flows through the pipeline

```
Transaction CSV
    ↓
Input validation
    ↓
Data loading and cleaning
    ↓
Behavioural feature engineering
    ↓
Rule-based scoring
    ↓
Model or hybrid scoring (if selected)
    ↓
Active risk score and risk level
    ↓
Alert priority and decision
    ↓
Dashboard analytics and investigation
    ↓
Downloadable scored results
```

---

## Required CSV columns

Uploaded files must contain these columns:

```
transaction_id
customer_id
timestamp
amount
currency
transaction_type
country
device_id
beneficiary_id
is_new_device
is_new_beneficiary
transactions_last_1h
account_age_days
customer_average_amount
customer_usual_country
is_fraud
```

A compatible sample file lives at `data/raw/sample_transactions.csv`.

---

## Upload validation

The validator rejects:

- empty files
- files with headers but no rows
- malformed CSVs
- files missing required columns
- blank or duplicate transaction IDs
- unsupported text encodings

Errors are shown in the dashboard — no silent failures, no stack traces visible to the user.

---

## Getting started

Clone the repo and move into the project folder:

```bash
git clone https://github.com/IYGabriel/fraud-risk-dashboard.git
cd fraud-risk-dashboard
```

Create and activate a virtual environment:

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the dashboard:

```bash
python -m streamlit run app.py
```

Then open the URL shown in your terminal — usually `http://localhost:8501`.

---

## Running the tests

```bash
pytest -v
```

The suite currently has **56 passing tests** covering data loading, feature engineering, fraud-rule scoring, alert decisions, dashboard utilities, upload validation, model-service behaviour, all three scoring modes, and end-to-end pipeline execution.

---

## Tech stack

- Python
- pandas
- Streamlit
- PyYAML
- pytest

---

## Design principles

The project is built around a few ideas: keep scoring logic separate from the dashboard, make rules configurable without code changes, make every component independently testable, and handle bad input gracefully. The model interface is a deliberate seam — replacing the placeholder with a real classifier shouldn't require restructuring anything.

---

## What it doesn't do (yet)

This is a portfolio and prototype application, not a production banking platform. It currently has no:

- trained machine-learning model (the Model and Hybrid modes use a placeholder)
- persistent database storage
- analyst authentication or role-based access
- case notes or case ownership
- sanctions or watchlist screening
- graph-based account and device analysis
- real-time event streaming
- model monitoring or drift detection
- external banking integrations

---

## Where it could go next

1. Train and integrate a real fraud-classification model
2. Add SHAP-based model explanations
3. Store alerts and decisions in PostgreSQL
4. Add case assignment, investigation notes, and resolution tracking
5. Expose the scoring pipeline through a FastAPI layer
6. Add real-time transaction ingestion
7. Introduce graph analysis across accounts and devices
8. Monitor model drift and performance over time
9. Add authentication and access controls
10. Feed analyst decisions back into model training

---

## Disclaimer

This project uses synthetic data and is intended for educational, research, and portfolio purposes. It should not be used to make real financial decisions without production-grade validation, governance, security, regulatory review, and model-risk controls.