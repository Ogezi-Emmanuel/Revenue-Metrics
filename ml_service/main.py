from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

# Initialize the Microservice
app = FastAPI(
    title="RevOps AI API Presentation Layer",
    description="Lightning-fast read-only API serving pre-calculated AI telemetry.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Notice: We no longer load the joblib models here.
# The Master Orchestrator handles all ML Inference during the ETL phase.


@app.get("/health")
def health_check():
    return {"status": "online", "system": "FastAPI Presentation Layer"}


@app.get("/api/v1/pipeline-diagnostics")
def get_pipeline_intelligence():
    try:
        # 1. DYNAMIC ANCHOR: Resolve the absolute path to the directory housing this file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(BASE_DIR, "synthetic_pipeline_payload.csv")

        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(
                f"Master CSV database not found at resolved path: {CSV_PATH}"
            )

        df = pd.read_csv(CSV_PATH)

        # Defensive Data Cleaning: Normalize stages to lowercase without spaces
        # This catches both HubSpot ('closedwon') and Salesforce ('Closed Won') formats
        df["stage_lower"] = (
            df["stage"].astype(str).str.lower().str.replace(" ", "")
        )
        open_pipe = df[
            ~df["stage_lower"].isin(["closedwon", "closedlost"])
        ].copy()

        # 1. Calculate 3-Tier Risk Tranches based on Orchestrator's pre-calculated numbers
        healthy_pipe = open_pipe[open_pipe["flight_risk_pct"] < 35.0]
        elevated_pipe = open_pipe[
            (open_pipe["flight_risk_pct"] >= 35.0)
            & (open_pipe["flight_risk_pct"] < 65.0)
        ]
        critical_pipe = open_pipe[open_pipe["flight_risk_pct"] >= 65.0]

        # 2. SORTING FIX: Prioritize Flight Risk first, Amount second.
        # This guarantees the most dangerous deals are always at the top of the queue.
        sorted_pipe = open_pipe.sort_values(
            by=["flight_risk_pct", "amount"], ascending=[False, False]
        )

        # 3. Construct the payload
        payload = {
            "metadata": {
                "total_open_arr": float(open_pipe["amount"].sum()),
                "total_active_deals": int(len(open_pipe)),
                "healthy": {
                    "count": int(len(healthy_pipe)),
                    "value": float(healthy_pipe["amount"].sum()),
                },
                "elevated": {
                    "count": int(len(elevated_pipe)),
                    "value": float(elevated_pipe["amount"].sum()),
                },
                "critical": {
                    "count": int(len(critical_pipe)),
                    "value": float(critical_pipe["amount"].sum()),
                },
            },
            "opportunities": sorted_pipe[
                [
                    "deal_name",
                    "company_name",
                    "stage",
                    "amount",
                    "flight_risk_pct",
                    "est_days_left",
                ]
            ].to_dict(orient="records"),
        }

        return payload

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Data Presentation failure: {str(e)}"
        )