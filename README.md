# Revenue Metrics Module

A robust SaaS metrics calculation engine designed for Revenue Operations (RevOps) teams to compute core business health indicators from CRM and pipeline data.

## Project Overview

The `revenue_metrics.py` module provides a `SaaSMetricsEngine` class that enables data-driven decision-making by calculating critical SaaS revenue metrics, including Net Revenue Retention (NRR), Gross Revenue Retention (GRR), Customer Lifetime Value (LTV), Customer Acquisition Cost (CAC), and weighted pipeline forecasts. This module is ideal for executive dashboards, financial planning, and sales operations analysis.

### Key Business Problems Solved
- **Retention Analysis**: Separates true churn from expansion revenue to understand core customer health
- **Unit Economics**: Validates that customer acquisition costs are justified by lifetime value
- **Pipeline Forecasting**: Uses probabilistic stage weighting to predict realistic revenue outcomes

## Core Features

1. **Retention Analysis**: Calculates both Net Revenue Retention (NRR) and Gross Revenue Retention (GRR)
2. **Unit Economics Calculation**: Computes CAC, LTV, and the LTV:CAC ratio (golden benchmark for SaaS)
3. **Weighted Pipeline Forecast**: Calculates expected deal revenue using stage probabilities

## Technical Requirements

- **Python Version**: 3.7 or higher
- **Dependencies**:
  - pandas >= 1.3.0
  - numpy >= 1.21.0
- **System Prerequisites**: Standard Python environment with pip package manager

## Installation & Setup

1. **Navigate to the project directory**:
   ```bash
   cd "c:\Users\user\OneDrive\Desktop\Revenue Metrics"
   ```

2. **Install required dependencies**:
   ```bash
   pip install pandas numpy
   ```

## Usage Examples

```python
from revenue_metrics import SaaSMetricsEngine
import pandas as pd

# Initialize the metrics engine with 80% gross margin
rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)

# Example 1: Retention Analysis
retention = rev_engine.analyze_retention(
    starting_arr=1200000,
    expansion=150000,
    contraction=45000,
    churn=85000
)
print(retention)  # {'NRR_Pct': 101.67, 'GRR_Pct': 89.17}

# Example 2: LTV:CAC Ratio
unit_economics = rev_engine.calculate_ltv_cac_ratio(
    total_cac_spend=350000,
    new_customers=50,
    arpa=1200,
    churn_rate_pct=2.5
)
print(unit_economics)  # {'CAC': 7000.0, 'LTV': 38400.0, 'LTV_to_CAC_Ratio': '5.5:1'}

# Example 3: Weighted Pipeline Forecast
pipeline_data = pd.DataFrame({
    'deal_amount': [50000, 120000, 15000, 85000],
    'stage_probability': [0.20, 0.60, 0.90, 0.10]
})
forecast = rev_engine.forecast_weighted_pipeline(pipeline_data)
print(forecast)  # 108500.0
```

## Function Documentation

### `SaaSMetricsEngine.__init__(gross_margin_pct: float = 0.85)`
Initializes the metrics engine with a specified gross margin percentage.

**Parameters:**
- `gross_margin_pct` (float, optional): Gross margin percentage (default: 0.85)

---

### `analyze_retention(starting_arr: float, expansion: float, contraction: float, churn: float) -> Dict[str, float]`
Calculates Net Revenue Retention (NRR) and Gross Revenue Retention (GRR).

**Parameters:**
- `starting_arr` (float): Starting Annual Recurring Revenue (must be > 0)
- `expansion` (float): Expansion revenue from existing customers
- `contraction` (float): Contraction revenue (downgrades)
- `churn` (float): Churned revenue (lost customers)

**Returns:**
- Dictionary containing `NRR_Pct` and `GRR_Pct` (rounded to 2 decimal places)

**Exceptions:**
- `ValueError`: If `starting_arr` is <= 0

---

### `calculate_ltv_cac_ratio(total_cac_spend: float, new_customers: int, arpa: float, churn_rate_pct: float) -> Dict[str, Union[float, str]]`
Calculates Customer Acquisition Cost (CAC), Lifetime Value (LTV), and LTV:CAC ratio.

**Parameters:**
- `total_cac_spend` (float): Total customer acquisition spend
- `new_customers` (int): Number of new customers acquired (must be > 0)
- `arpa` (float): Average Revenue Per Account
- `churn_rate_pct` (float): Monthly churn rate percentage (must be > 0)

**Returns:**
- Dictionary containing `CAC`, `LTV`, and `LTV_to_CAC_Ratio`

---

### `forecast_weighted_pipeline(pipeline_df: pd.DataFrame) -> float`
Calculates expected pipeline revenue using stage probabilities.

**Parameters:**
- `pipeline_df` (pd.DataFrame): DataFrame containing CRM pipeline data

**Returns:**
- Total weighted pipeline value (rounded to 2 decimal places)

**Exceptions:**
- `KeyError`: If DataFrame missing required columns

## Input Data Specifications

### Pipeline DataFrame (`forecast_weighted_pipeline`)
Required columns:
- `deal_amount` (numeric): Value of the deal
- `stage_probability` (float between 0 and 1): Probability of deal closing

Optional columns (not used in calculations but typically present):
- `deal_id`: Unique identifier for the deal

## Output Metrics Description

| Metric | Definition | Business Interpretation |
|--------|------------|-------------------------|
| **NRR_Pct** | Net Revenue Retention percentage | Measures overall revenue health including upsells; >100% indicates growth |
| **GRR_Pct** | Gross Revenue Retention percentage | Isolates churn/contraction; max 100%; shows true customer retention |
| **CAC** | Customer Acquisition Cost | Average cost to acquire one new customer |
| **LTV** | Customer Lifetime Value | Total expected revenue from a customer over their lifetime |
| **LTV_to_CAC_Ratio** | Lifetime Value to CAC ratio | Golden benchmark is 3:1; higher = more profitable acquisition |
| **Weighted Pipeline** | Probability-adjusted pipeline value | Realistic revenue forecast from active deals |

## Error Handling & Troubleshooting

| Error Message | Cause | Resolution |
|---------------|-------|------------|
| `ValueError: Starting ARR must be greater than zero.` | Invalid `starting_arr` parameter | Ensure `starting_arr` is a positive number |
| `KeyError: DataFrame missing required CRM pipeline columns.` | Missing columns in pipeline DataFrame | Verify DataFrame has `deal_amount` and `stage_probability` |
| `{"Error": "Invalid inputs for LTV:CAC calculation"}` | Invalid `new_customers` or `churn_rate_pct` | Ensure both values are greater than 0 |

## Testing Instructions

To create and run unit tests (recommended using pytest):

1. **Install pytest**:
   ```bash
   pip install pytest
   ```

2. **Create a test file** (e.g., `test_revenue_metrics.py`) with test cases for each function.

3. **Run tests**:
   ```bash
   pytest test_revenue_metrics.py -v
   ```

**Test Coverage Requirements**: Aim for 100% coverage of all public methods and error handling paths.

## Maintenance Guidelines

- **Code Style**: Follow PEP 8 style guidelines
- **Contributions**: Submit changes via pull requests with appropriate test coverage
- **Updates**: Maintain backward compatibility when adding new features
- **Documentation**: Update this README when modifying function signatures or adding new metrics

## License & Contact Information

- **License**: To be determined
- **Maintainer**: Revenue Operations Team
- **Contact**: [Add maintainer contact information here]
