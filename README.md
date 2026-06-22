# RevOps AI Command Center

A comprehensive, enterprise-grade Revenue Operations platform that combines:
- Synthetic data generation
- Dual-engine ML inference (churn prediction + velocity regression)
- CRM integration (HubSpot and Salesforce)
- Executive dashboard visualization

---

## Table of Contents
1. [Project Purpose](#project-purpose)
2. [Core Functionality](#core-functionality)
3. [Technical Stack](#technical-stack)
4. [Directory Structure](#directory-structure)
5. [Getting Started](#getting-started)
6. [Usage Instructions](#usage-instructions)
7. [Features](#features)
8. [Troubleshooting](#troubleshooting)
9. [Contributing Guidelines](#contributing-guidelines)
10. [License and Contact](#license-and-contact)

---

## Project Purpose
This platform enables RevOps teams to:
1. Generate realistic B2B SaaS pipeline datasets
2. Predict deal churn risk using ML
3. Forecast sales cycle velocity
4. Sync predictions to CRM systems (HubSpot/Salesforce)
5. Visualize pipeline health in a dark-theme executive dashboard

---

## Core Functionality
- **Dual-Engine ML Models**: Random Forest Classifier (churn) and Regressor (velocity)
- **Forward ETL**: Extract live deals from HubSpot/Salesforce
- **Reverse ETL**: Push AI predictions back to CRM
- **Executive Dashboard**: Real-time visualization of pipeline health with live API (hosted on Render)

---

## Technical Stack
### Backend
- **API Framework**: FastAPI 0.104.1
- **ML Library**: Scikit-learn 1.3.2
- **Data Processing**: Pandas 2.1.3
- **Model Serialization**: Joblib 1.3.2
- **ASGI Server**: Uvicorn 0.24.0.post1

### Integrations
- **HubSpot**: Private App API
- **Salesforce**: simple-salesforce 1.12.5
- **HTTP Client**: Requests 2.31.0

### Frontend
- **Vanilla JavaScript**: No build tools required
- **Charting**: Chart.js (via CDN)
- **Styling**: Tailwind CSS (via CDN)
- **Font**: Google Fonts Inter

---

## Directory Structure
```
revenue-metrics/
├── etl_pipeline/
│   ├── hubspot_controller.py       # HubSpot forward/reverse ETL
│   ├── salesforce_controller.py    # Salesforce forward/reverse ETL
│   ├── master_orchestrator.py      # Full-loop sync orchestrator
│   ├── generate_pipeline.py        # Synthetic data generation
│   └── provision_hubspot.py        # Auto-provision HubSpot custom properties
├── ml_service/
│   ├── main.py                     # FastAPI ML inference server
│   ├── revenue_metrics.py          # SaaS KPI calculations
│   ├── train_models.py             # ML model training script
│   ├── revops_churn_model.joblib   # Trained churn classifier
│   └── revops_velocity_regressor.joblib  # Trained velocity regressor
├── frontend/
│   ├── index.html                  # Main dashboard
│   ├── styles.css                  # Custom styling
│   └── app.js                      # Frontend logic
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## Getting Started
### Prerequisites
- Python 3.8+
- Valid HubSpot Private App token (if using HubSpot)
- Valid Salesforce credentials (if using Salesforce)

---

### 1. Clone the Repository
```bash
git clone https://github.com/Ogezi-Emmanuel/Revenue-Metrics.git
cd Revenue-Metrics
```

---

### 2. Create and Activate Virtual Environment (Recommended)
#### Windows
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Create Environment File
Create a `.env` file in the project root directory:
```env
# HubSpot Configuration
HUBSPOT_PRIVATE_TOKEN=your_hubspot_private_app_token

# Salesforce Configuration
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
```

---

### 5. Generate Synthetic Data
```bash
cd etl_pipeline
python generate_pipeline.py
```
This creates `synthetic_pipeline_payload.csv` in both `etl_pipeline/` and `ml_service/` directories.

---

## Usage Instructions

### Option A: Use Live Dashboard
1. **Open Dashboard**
Open `frontend/index.html` in any browser - it will connect to the live API hosted on Render!

### Option B: Run ML Service and Dashboard (Standalone)
1. **Update API_URL** (in `frontend/app.js`)
Change the API_URL from `https://revops-inference-engines.onrender.com` to `http://127.0.0.1:8000`

2. **Start FastAPI Server**
```bash
cd ml_service
uvicorn main:app --reload
```

3. **Open Dashboard**
Open `frontend/index.html` in any browser.

---

### Option C: Full-Loop CRM Sync
#### Step 1: Provision HubSpot Custom Property (HubSpot Only)
```bash
cd etl_pipeline
python provision_hubspot.py
```

#### Step 2: Run Full Sync
```bash
# For HubSpot
python -m master_orchestrator --target hubspot

# For Salesforce
python -m master_orchestrator --target salesforce
```

---

### Option D: Retrain ML Models
```bash
cd ml_service
python train_models.py
```
Requires `synthetic_pipeline_payload.csv` in the `ml_service/` directory.

---

## Features

### 1. Synthetic Data Generation
- Creates realistic B2B SaaS deals
- Includes: company names, deal amounts, stages, sales owners, ML features
- 3000 records by default (configurable)

### 2. Dual-Engine ML Inference
- **Churn Risk Classifier**: Probability deal will be lost
- **Velocity Regressor**: Predicts total sales cycle length

### 3. CRM Integration
- **HubSpot**: Full forward and reverse ETL
- **Salesforce**: Full forward and reverse ETL
- Auto-provisioning of custom properties (HubSpot)

### 4. Executive Dashboard (Live on Render)
- **URL**: Frontend can be opened directly in browser, connects to live API at `https://revops-inference-engines.onrender.com`
- Dark theme with neon accents
- 3-tier risk KPI cards (Healthy, Elevated, Critical) showing deal count and value
- Interactive Flight Risk Matrix scatter plot (click points to locate deals)
- Search/filter bar to find specific accounts
- Grid of deal cards with AI churn vector, valuation, and days left
- Custom scrollbars and glassmorphism effects

---

## Troubleshooting

### Common Issues
1. **FastAPI won't start**: Make sure you're in `ml_service/` and run `uvicorn main:app --reload`
2. **Missing CSV**: Run `generate_pipeline.py` in `etl_pipeline/`
3. **Reverse ETL failing**: Verify custom CRM properties exist (use `provision_hubspot.py` for HubSpot)
4. **HubSpot API errors**: Check HUBSPOT_PRIVATE_TOKEN in `.env` and scopes (needs `crm.objects.deals.write`)

---

## Contributing Guidelines
1. Follow PEP 8 style for Python code
2. Test changes thoroughly
3. Update this README if features are added or changed
4. Never commit `.env` to Git
5. Submit changes via PR (if using Git)

---

## License and Contact

- **License**: [MIT License](https://opensource.org/licenses/MIT)
- **Maintainer**: Ogezi Emmanuel
- **Email**: emmanuel@emmanuelogezi.cv
- **LinkedIn**: [https://www.linkedin.com/in/emmanuel-ogezi-2501932b6/](https://www.linkedin.com/in/emmanuel-ogezi-2501932b6/)
