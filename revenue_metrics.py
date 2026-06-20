import pandas as pd
import numpy as np
from typing import Dict, Union

class SaaSMetricsEngine:
    """
    A robust data processing engine to calculate core RevOps metrics.
    Designed to ingest CRM pipeline data and output executive health scores.
    """
    
    def __init__(self, gross_margin_pct: float = 0.85):
        self.gross_margin = gross_margin_pct

    def analyze_retention(self, starting_arr: float, expansion: float, contraction: float, churn: float) -> Dict[str, float]:
        """
        Calculates both Net Revenue Retention (NRR) and Gross Revenue Retention (GRR).
        GRR ignores expansion, exposing the true churn rate of the base.
        """
        if starting_arr <= 0:
            raise ValueError("Starting ARR must be greater than zero.")

        # NRR includes expansion.
        nrr = ((starting_arr + expansion - contraction - churn) / starting_arr) * 100
        
        # GRR strictly isolates losses. It cannot exceed 100%.
        grr = ((starting_arr - contraction - churn) / starting_arr) * 100
        
        return {
            "NRR_Pct": round(nrr, 2),
            "GRR_Pct": round(min(grr, 100.0), 2) # Cap at 100% per SaaS standards
        }

    def calculate_ltv_cac_ratio(self, total_cac_spend: float, new_customers: int, arpa: float, churn_rate_pct: float) -> Dict[str, Union[float, str]]:
        """
        Calculates Customer Acquisition Cost (CAC), Lifetime Value (LTV), and the LTV:CAC Ratio.
        The golden benchmark for B2B SaaS is a 3:1 ratio.
        """
        if new_customers <= 0 or churn_rate_pct <= 0:
            return {"Error": "Invalid inputs for LTV:CAC calculation"}

        # 1. Calculate CAC
        cac = total_cac_spend / new_customers
        
        # 2. Calculate Customer Lifetime in months (1 / churn_rate)
        lifetime_months = 1 / (churn_rate_pct / 100)
        
        # 3. Calculate LTV (Lifetime Value) factored by gross margin
        ltv = (arpa * lifetime_months) * self.gross_margin
        
        # 4. The Golden Ratio
        ltv_cac_ratio = ltv / cac

        return {
            "CAC": round(cac, 2),
            "LTV": round(ltv, 2),
            "LTV_to_CAC_Ratio": f"{round(ltv_cac_ratio, 1)}:1"
        }

    def forecast_weighted_pipeline(self, pipeline_df: pd.DataFrame) -> float:
        """
        Ingests a Pandas DataFrame of active CRM deals and calculates the expected revenue
        using probabilistic stage weighting.
        Expected Columns: ['deal_amount', 'stage_probability']
        """
        if not {'deal_amount', 'stage_probability'}.issubset(pipeline_df.columns):
            raise KeyError("DataFrame missing required CRM pipeline columns.")
            
        # Vectorized calculation for expected value
        pipeline_df['expected_value'] = pipeline_df['deal_amount'] * pipeline_df['stage_probability']
        total_weighted_pipeline = pipeline_df['expected_value'].sum()
        
        return round(total_weighted_pipeline, 2)


if __name__ == "__main__":
    # Initialize Engine
    rev_engine = SaaSMetricsEngine(gross_margin_pct=0.80)

    print("=== BOOTING AI REVENUE COMMAND CENTER ===")
    
    # 1. Load the Generated CSV Data
    try:
        live_pipeline = pd.read_csv("synthetic_pipeline_payload.csv")
        print(f"SUCCESS: Ingested {len(live_pipeline)} live pipeline records.\n")
    except FileNotFoundError:
        print("CRITICAL ERROR: 'synthetic_pipeline_payload.csv' not found.")
        exit()

    # 2. Schema Translation: Map HubSpot/Salesforce stages to close probabilities
    probability_map = {
        'closedwon': 1.0,
        'contractsent': 0.85,
        'decisionmakerboughtin': 0.60,
        'presentationscheduled': 0.40,
        'qualifiedtobuy': 0.20,
        'appointmentscheduled': 0.10,
        'closedlost': 0.0
    }

    # Apply the probability mapping
    live_pipeline['stage_probability'] = live_pipeline['stage'].map(probability_map)
    
    # Rename 'amount' to 'deal_amount' to satisfy the engine's strict column requirement
    live_pipeline = live_pipeline.rename(columns={'amount': 'deal_amount'})

    # 3. Data Cleansing: Isolate the Open Pipeline
    # A RevOps forecast only looks at active deals, not deals already won or lost
    open_pipeline = live_pipeline[~live_pipeline['stage'].isin(['closedwon', 'closedlost'])].copy()

    # 4. Engine Execution
    raw_open_pipe = open_pipeline['deal_amount'].sum()
    forecast = rev_engine.forecast_weighted_pipeline(open_pipeline)
    
    # Calculate actual revenue secured in the dataset
    secured_arr = live_pipeline[live_pipeline['stage'] == 'closedwon']['deal_amount'].sum()

    # --- Executive Output ---
    print("=== REAL-TIME ENTERPRISE DIAGNOSTICS ===")
    print(f"Total Secured ARR:     ${secured_arr:,.2f}")
    print(f"Raw Open Pipeline:     ${raw_open_pipe:,.2f}")
    print(f"Weighted Q3 Forecast:  ${forecast:,.2f}")