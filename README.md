# Revenue Metrics & CRM Pipeline Project

A comprehensive SaaS metrics and CRM data pipeline project that combines advanced revenue analytics with enterprise-grade CRM integration for both HubSpot and Salesforce. This end-to-end solution includes synthetic data generation, schema management, CRM data ingestion, and executive health score calculation.

## Project Overview

This project provides a complete data pipeline for Revenue Operations (RevOps) teams, enabling:

1. **Synthetic Data Generation**: Create realistic B2B SaaS pipeline datasets with ML telemetry features
2. **CRM Integration**: Seamless integration with both HubSpot and Salesforce CRM platforms
3. **Data Ingestion**: Automated relational data sync with rate limiting and error handling
4. **Revenue Analytics**: Calculate core SaaS metrics including NRR, GRR, LTV, CAC, and weighted pipeline forecasts
5. **Schema Management**: Programmatically set up and manage custom CRM properties

### Key Business Problems Solved
- **Pipeline Data Scarcity**: Generate realistic synthetic data for testing and demonstration
- **Multi-CRM Management**: Unified interface for working with both HubSpot and Salesforce
- **Data Quality & Consistency**: Ensures proper relational data binding between companies, contacts, and deals
- **Retention Analysis**: Separates true churn from expansion revenue to understand core customer health
- **Unit Economics**: Validates that customer acquisition costs are justified by lifetime value
- **Pipeline Forecasting**: Uses probabilistic stage weighting to predict realistic revenue outcomes

## Core Features

1. **Synthetic Pipeline Generation**: Create 1000s of realistic B2B SaaS deals with ML telemetry
2. **HubSpot Schema Setup**: Programmatically create custom deal properties
3. **HubSpot Multi-Object Sync**: Relational sync of companies, contacts, and deals with rate limiting
4. **Salesforce Enterprise Sync**: Full Salesforce integration with Opportunity, Account, and Contact creation
5. **CRM Connection Testing**: Test connectivity for both HubSpot and Salesforce
6. **CRM Data Extraction**: Extract pipeline data from HubSpot
7. **Revenue Metrics Calculation**: Compute NRR, GRR, LTV, CAC, and weighted pipeline forecasts

## Technical Requirements

- **Python Version**: 3.7 or higher
- **Dependencies**:
  - pandas >= 1.3.0
  - numpy >= 1.21.0
  - python-dotenv >= 1.0.0
  - simple-salesforce >= 1.11.0
  - requests >= 2.31.0
  - Faker >= 18.0.0
- **System Prerequisites**: Standard Python environment with pip package manager
- **CRM Accounts**: Active HubSpot and/or Salesforce accounts with API access

## Installation & Setup

1. **Clone the repository from GitHub**:
   ```bash
   git clone https://github.com/username/revenue-metrics.git
   cd revenue-metrics
   ```
   *(Replace `username/revenue-metrics` with your actual GitHub repository path)*

2. **Install required dependencies**:
   ```bash
   pip install pandas numpy python-dotenv simple-salesforce requests Faker
   ```

3. **Configure Environment Variables**:
   - Create a `.env` file in the project root directory
   - Add your CRM credentials (see Environment Variable Configuration section below)

## Environment Variable Configuration

Create a `.env` file in your project root with the following variables:

```env
# HubSpot Configuration
HUBSPOT_PRIVATE_TOKEN="your-hubspot-private-app-token"

# Salesforce Configuration
SF_USERNAME="your-salesforce-username"
SF_PASSWORD="your-salesforce-password"
SF_SECURITY_TOKEN="your-salesforce-security-token"
```

**Where to find credentials:**
- **HubSpot Private Token**: Create a private app in HubSpot Settings → Integrations → Private Apps
- **Salesforce Credentials**: Use your Salesforce login and security token (available in Salesforce Settings → My Personal Information → Reset My Security Token)

## Project Structure

```
revenue-metrics/
├── revenue_metrics.py          # Core SaaS metrics engine
├── generate_pipeline.py        # Synthetic pipeline data generation
├── setup_schema.py             # HubSpot custom property setup
├── enterprise_hubspot_sync.py  # HubSpot multi-object sync
├── sf_enterprise_sync.py       # Salesforce enterprise sync
├── crm_extraction.py           # HubSpot data extraction
├── sf_connection_test.py       # Salesforce connection test
└── synthetic_pipeline_payload.csv (generated)
```

## Pipeline Workflow

The complete pipeline workflow consists of these steps:

1. **Generate Data**: Create synthetic pipeline dataset
2. **Setup Schema** (HubSpot only): Create custom properties
3. **Sync to CRM**: Load data into HubSpot or Salesforce
4. **Analyze**: Calculate revenue metrics

## Usage Examples

### Complete Pipeline Execution (HubSpot)

```python
# Step 1: Generate synthetic pipeline data
from generate_pipeline import generate_saas_deals
pipeline_df = generate_saas_deals(3000)
pipeline_df.to_csv("synthetic_pipeline_payload.csv", index=False)

# Step 2: Setup HubSpot custom schema (run once)
import setup_schema  # Executes schema setup when imported

# Step 3: Sync data to HubSpot
import enterprise_hubspot_sync  # Executes sync when imported

# Step 4: Calculate revenue metrics
from revenue_metrics import SaaSMetricsEngine
rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)
```

### Complete Pipeline Execution (Salesforce)

```python
# Step 1: Generate synthetic pipeline data
from generate_pipeline import generate_saas_deals
pipeline_df = generate_saas_deals(400)  # Smaller dataset for Salesforce
pipeline_df.to_csv("synthetic_pipeline_payload.csv", index=False)

# Step 2: Sync data to Salesforce
from sf_enterprise_sync import run_salesforce_ingestion
run_salesforce_ingestion("synthetic_pipeline_payload.csv", record_limit=400)

# Step 3: Calculate revenue metrics
from revenue_metrics import SaaSMetricsEngine
rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)
```

### Individual Module Usage

#### Revenue Metrics (Basic Usage)

```python
from revenue_metrics import SaaSMetricsEngine
import pandas as pd

rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)

# Retention Analysis
retention = rev_engine.analyze_retention(
    starting_arr=1200000,
    expansion=150000,
    contraction=45000,
    churn=85000
)
print(retention)  # {'NRR_Pct': 101.67, 'GRR_Pct': 89.17}

# LTV:CAC Ratio
unit_economics = rev_engine.calculate_ltv_cac_ratio(
    total_cac_spend=350000,
    new_customers=50,
    arpa=1200,
    churn_rate_pct=2.5
)
print(unit_economics)  # {'CAC': 7000.0, 'LTV': 38400.0, 'LTV_to_CAC_Ratio': '5.5:1'}

# Weighted Pipeline Forecast (Simple)
pipeline_data = pd.DataFrame({
    'deal_amount': [50000, 120000, 15000, 85000],
    'stage_probability': [0.20, 0.60, 0.90, 0.10]
})
forecast = rev_engine.forecast_weighted_pipeline(pipeline_data)
print(forecast)  # 108500.0
```

#### Revenue Metrics (Full Pipeline Integration)

Run the built-in full pipeline example that ingests CSV data, maps stages to probabilities, and calculates executive diagnostics:

```python
# Option 1: Run directly as a script
python revenue_metrics.py

# Option 2: Use the full pipeline programmatically
from revenue_metrics import SaaSMetricsEngine
import pandas as pd

# Initialize engine
rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)

# Load and prepare pipeline data
live_pipeline = pd.read_csv("synthetic_pipeline_payload.csv")

# Map CRM stages to close probabilities
probability_map = {
    'closedwon': 1.0,
    'contractsent': 0.85,
    'decisionmakerboughtin': 0.60,
    'presentationscheduled': 0.40,
    'qualifiedtobuy': 0.20,
    'appointmentscheduled': 0.10,
    'closedlost': 0.0
}

# Prepare data for engine
live_pipeline['stage_probability'] = live_pipeline['stage'].map(probability_map)
live_pipeline = live_pipeline.rename(columns={'amount': 'deal_amount'})

# Isolate open pipeline (exclude closed deals)
open_pipeline = live_pipeline[~live_pipeline['stage'].isin(['closedwon', 'closedlost'])].copy()

# Calculate metrics
raw_open_pipe = open_pipeline['deal_amount'].sum()
forecast = rev_engine.forecast_weighted_pipeline(open_pipeline)
secured_arr = live_pipeline[live_pipeline['stage'] == 'closedwon']['deal_amount'].sum()

# Print diagnostics
print("=== REAL-TIME ENTERPRISE DIAGNOSTICS ===")
print(f"Total Secured ARR:     ${secured_arr:,.2f}")
print(f"Raw Open Pipeline:     ${raw_open_pipe:,.2f}")
print(f"Weighted Q3 Forecast:  ${forecast:,.2f}")
```

#### Synthetic Data Generation

```python
from generate_pipeline import generate_saas_deals

# Generate 3000 realistic SaaS deals
pipeline_df = generate_saas_deals(num_records=3000)
pipeline_df.to_csv("synthetic_pipeline_payload.csv", index=False)
```

#### Connection Testing

```bash
# Test Salesforce connection
python sf_connection_test.py

# Test HubSpot extraction
python crm_extraction.py
```

## Module Documentation

### revenue_metrics.py - SaaSMetricsEngine

#### `SaaSMetricsEngine.__init__(gross_margin_pct: float = 0.85)`
Initializes the metrics engine with a specified gross margin percentage.

**Parameters:**
- `gross_margin_pct` (float, optional): Gross margin percentage (default: 0.85)

---

#### `analyze_retention(starting_arr: float, expansion: float, contraction: float, churn: float) -> Dict[str, float]`
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

#### `calculate_ltv_cac_ratio(total_cac_spend: float, new_customers: int, arpa: float, churn_rate_pct: float) -> Dict[str, Union[float, str]]`
Calculates Customer Acquisition Cost (CAC), Lifetime Value (LTV), and LTV:CAC ratio.

**Parameters:**
- `total_cac_spend` (float): Total customer acquisition spend
- `new_customers` (int): Number of new customers acquired (must be > 0)
- `arpa` (float): Average Revenue Per Account
- `churn_rate_pct` (float): Monthly churn rate percentage (must be > 0)

**Returns:**
- Dictionary containing `CAC`, `LTV`, and `LTV_to_CAC_Ratio`

---

#### `forecast_weighted_pipeline(pipeline_df: pd.DataFrame) -> float`
Calculates expected pipeline revenue using stage probabilities.

**Parameters:**
- `pipeline_df` (pd.DataFrame): DataFrame containing CRM pipeline data

**Returns:**
- Total weighted pipeline value (rounded to 2 decimal places)

**Exceptions:**
- `KeyError`: If DataFrame missing required columns

### generate_pipeline.py

#### `generate_saas_deals(num_records: int = 3000) -> pd.DataFrame`
Generates a synthetic dataset of B2B SaaS deals with realistic distributions and ML telemetry.

**Parameters:**
- `num_records` (int, optional): Number of deals to generate (default: 3000)

**Returns:**
- DataFrame with columns: deal_name, company_name, deal_type, amount, stage, sales_owner, days_stalled, rep_touchpoints, client_engagement_index

### setup_schema.py

#### `create_custom_deal_property(name: str, label: str, property_type: str, field_type: str)`
Creates a custom deal property in HubSpot.

**Parameters:**
- `name` (str): Internal property name
- `label` (str): Human-readable label
- `property_type` (str): HubSpot property type (e.g., "number")
- `field_type` (str): HubSpot field type (e.g., "number")

### enterprise_hubspot_sync.py

#### `relational_sync_pipeline(row: pd.Series) -> bool`
Syncs a single deal record to HubSpot with full relational binding (company → contact → deal).

**Parameters:**
- `row` (pd.Series): Single row from pipeline DataFrame

**Returns:**
- bool: True if sync successful, False otherwise

#### `execute_request_with_backoff(method: str, url: str, payload: dict = None, max_retries: int = 3)`
Handles API requests with automatic backoff for HubSpot rate limits.

### sf_enterprise_sync.py

#### `run_salesforce_ingestion(csv_path: str, record_limit: int = 400)`
Ingests pipeline data into Salesforce with Account, Contact, and Opportunity creation.

**Parameters:**
- `csv_path` (str): Path to pipeline CSV file
- `record_limit` (int, optional): Maximum records to process (default: 400)

## Input Data Specifications

### Pipeline DataFrame

Required columns for CRM sync:
- `deal_name` (str): Name of the deal
- `company_name` (str): Company name
- `deal_type` (str): "newbusiness" or "existingbusiness"
- `amount` (numeric): Deal amount
- `stage` (str): Pipeline stage (HubSpot or Salesforce format)
- `sales_owner` (str): Sales rep name
- `days_stalled` (int): Days deal has been stalled
- `rep_touchpoints` (int): Number of rep interactions
- `client_engagement_index` (float): 0.0-1.0 engagement score

### Revenue Metrics Pipeline DataFrame

Required columns for `forecast_weighted_pipeline`:
- `deal_amount` (numeric): Value of the deal
- `stage_probability` (float between 0 and 1): Probability of deal closing

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
| `KeyError: DataFrame missing required CRM pipeline columns.` | Missing columns in pipeline DataFrame | Verify DataFrame has required columns |
| `{"Error": "Invalid inputs for LTV:CAC calculation"}` | Invalid `new_customers` or `churn_rate_pct` | Ensure both values are greater than 0 |
| `CRITICAL: Authentication failed.` | Invalid Salesforce credentials | Verify Salesforce username, password, and security token in .env |
| `API Error 401` | Invalid HubSpot token | Verify HUBSPOT_PRIVATE_TOKEN in .env |
| `Rate Limit Hit` | HubSpot API rate limiting | Automatic backoff handles this; wait for completion |

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

4. **Test CRM connections**:
   ```bash
   python sf_connection_test.py
   python crm_extraction.py
   ```

**Test Coverage Requirements**: Aim for 100% coverage of all public methods and error handling paths.

## Maintenance Guidelines

- **Code Style**: Follow PEP 8 style guidelines
- **Security**: Never commit `.env` file or sensitive credentials to Git
- **Contributions**: Submit changes via pull requests with appropriate test coverage
- **Updates**: Maintain backward compatibility when adding new features
- **Documentation**: Update this README when modifying function signatures or adding new metrics

## Changelog

All notable changes to this project will be documented in this section.

### v1.1.0 (2026-06-20)
- **Enhanced `revenue_metrics.py` main block**: Added full pipeline integration example with CSV ingestion, schema mapping, and data cleansing
- **Updated documentation**: Expanded README with comprehensive usage examples and Changelog
- **Improved .gitignore**: Added proper exclusions for environment files and data

### v1.0.0 (Initial Release)
- Initial project structure with core modules:
  - Revenue metrics calculation (NRR, GRR, LTV, CAC, weighted pipeline)
  - Synthetic pipeline data generation
  - HubSpot schema setup and multi-object sync
  - Salesforce enterprise sync
  - Connection testing tools

## License & Contact Information

- **License**: MIT License
- **Maintainer**: Revenue Operations Team
- **Contact**: [https://www.linkedin.com/in/emmanuel-ogezi-2501932b6/]
