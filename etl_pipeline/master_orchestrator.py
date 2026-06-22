import argparse
import pandas as pd
import joblib
import os
import sys

# Import your CRM controllers
import hubspot_controller
import salesforce_controller

def run_orchestrator(target_crm: str):
    print(f"=== REVOPS AI MASTER ORCHESTRATOR ===")
    print(f"Targeting Architecture: {target_crm.upper()}\n")

    # 1. FORWARD ETL (Extraction)
    try:
        if target_crm == "hubspot":
            df = hubspot_controller.extract_pipeline()
        elif target_crm == "salesforce":
            df = salesforce_controller.extract_pipeline()
        else:
            raise ValueError("Unsupported CRM target.")
            
        if df.empty:
            print("Pipeline is empty. Terminating sync.")
            sys.exit()
    except Exception as e:
        print(f"CRITICAL EXTRACTION ERROR: {e}")
        sys.exit()

    # 2. AI INFERENCE (The Dual-Engine Brain)
    print("\n[AI ENGINE] Booting Dual-Engine ML Models...")
    try:
        churn_path = os.path.join("..", "ml_service", "revops_churn_model.joblib")
        velocity_path = os.path.join("..", "ml_service", "revops_velocity_regressor.joblib")
        
        churn_model = joblib.load(churn_path)
        velocity_model = joblib.load(velocity_path)
    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: Could not find ML models. Details: {e}")
        sys.exit()

    print("[AI ENGINE] Calculating Churn Vectors and Sales Velocity...")
    
    # Run Churn
    features_churn = ['amount', 'days_stalled', 'rep_touchpoints', 'client_engagement_index']
    churn_probs = churn_model.predict_proba(df[features_churn])[:, 1]
    df['calculated_flight_risk'] = (churn_probs * 100).round(1)
    
    # Run Velocity
    features_velocity = ['amount', 'rep_touchpoints', 'client_engagement_index']
    predicted_days = velocity_model.predict(df[features_velocity])
    df['predicted_cycle_days'] = predicted_days.round(0)
    
    # Math: Estimated days left = Total predicted cycle - Days already stalled
    df['est_days_left'] = (df['predicted_cycle_days'] - df['days_stalled']).clip(lower=1)
    
   # 3. FASTAPI STATE UPDATE (Smart Upsert Merge)
    print(f"[DATA LAKE] Merging {target_crm.upper()} telemetry into Master Pipeline...")
    
    # Tag the fresh data so we know where it came from
    df['crm_source'] = target_crm
    df['flight_risk_pct'] = df['calculated_flight_risk'] 
    
    csv_path = os.path.join("..", "ml_service", "synthetic_pipeline_payload.csv")
    
    # If the master database already exists, perform a surgical merge
    if os.path.exists(csv_path):
        master_df = pd.read_csv(csv_path)
        
        # Identify if we have legacy data from this specific CRM and purge it
        if 'crm_source' in master_df.columns:
            master_df = master_df[master_df['crm_source'] != target_crm]
        
        # Append the fresh data to the untouched data from the other CRM
        final_df = pd.concat([master_df, df], ignore_index=True)
    else:
        # If it's the first time running, this becomes the master
        final_df = df

    # Lock in the global state
    final_df.to_csv(csv_path, index=False)
    print(f"[DATA LAKE] Global state updated. Total active deals across all CRMs: {len(final_df)}")
    
    # 4. REVERSE ETL (Patching)
    print()
    if target_crm == "hubspot":
        hubspot_controller.patch_pipeline(df)
    elif target_crm == "salesforce":
        salesforce_controller.patch_pipeline(df)

    print("\n=== FULL LOOP SYNC COMPLETE ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute the RevOps AI full-loop sync.")
    parser.add_argument(
        "--target", 
        type=str, 
        choices=["hubspot", "salesforce"], 
        required=True, 
        help="Specify which CRM to synchronize (hubspot or salesforce)"
    )
    
    args = parser.parse_args()
    run_orchestrator(args.target)