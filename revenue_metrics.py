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

    # 1. Retention Analysis
    retention_scores = rev_engine.analyze_retention(
        starting_arr=1200000, 
        expansion=150000, 
        contraction=45000, 
        churn=85000
    )
    
    # 2. Unit Economics (LTV:CAC)
    unit_economics = rev_engine.calculate_ltv_cac_ratio(
        total_cac_spend=350000, 
        new_customers=50, 
        arpa=1200, 
        churn_rate_pct=2.5
    )

    # 3. Probabilistic Pipeline Forecast (Simulating CRM Data)
    mock_pipeline = pd.DataFrame({
        'deal_id': [101, 102, 103, 104],
        'deal_amount': [50000, 120000, 15000, 85000],
        'stage_probability': [0.20, 0.60, 0.90, 0.10] # e.g., 20% likely to close
    })
    
    forecast = rev_engine.forecast_weighted_pipeline(mock_pipeline)

    # --- Executive Output ---
    print("=== AI REVENUE COMMAND CENTER: DIAGNOSTICS ===")
    print(f"Retention Health: {retention_scores}")
    print(f"Unit Economics:   {unit_economics}")
    print(f"Weighted Q3 Pipe: ${forecast:,.2f}")