import pandas as pd
import time
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from simple_salesforce import Salesforce, exceptions

load_dotenv()

def get_sf_connection():
    return Salesforce(
        username=os.getenv("SF_USERNAME"), 
        password=os.getenv("SF_PASSWORD"), 
        security_token=os.getenv("SF_SECURITY_TOKEN")
    )

def extract_pipeline():
    """FORWARD ETL: Pulls all live Salesforce Opportunities via SOQL."""
    print("[SALESFORCE] Authenticating and querying active pipeline...")
    sf = get_sf_connection()
    
    # SOQL Query to grab ALL open opportunities (Limit removed)
    query = """
        SELECT Id, Name, Account.Name, Amount, StageName, LastModifiedDate 
        FROM Opportunity 
        WHERE IsClosed = False
    """
    
    # query_all() automatically handles Salesforce's 2000-record pagination limits
    result = sf.query_all(query)
    records = result.get('records', [])
    print(f"Fetched {len(records)} deals from Salesforce database...")
    
    ml_ready_data = []
    now = datetime.now(timezone.utc)
    
    for opp in records:
        # Financials
        raw_amount = opp.get('Amount')
        clean_amount = float(raw_amount) if raw_amount else 0.0
        
        # Derive days stalled based on Last Modified Date
        try:
            last_modified_str = opp.get('LastModifiedDate')
            if last_modified_str:
                last_modified = datetime.strptime(last_modified_str, "%Y-%m-%dT%H:%M:%S.000+0000").replace(tzinfo=timezone.utc)
                days_stalled = max(1, (now - last_modified).days)
            else:
                days_stalled = 1
        except Exception:
            days_stalled = 1

        # Heuristic Engagement Algorithm (Baseline assumption for SF without complex subqueries)
        touchpoints = 2 # Standardized baseline if activities aren't explicitly queried
        raw_engagement = 5.0 + (touchpoints * 0.5) - (days_stalled * 0.2)
        client_engagement_index = max(1.0, min(10.0, round(raw_engagement, 1))) / 10.0

        ml_ready_data.append({
            "crm_id": opp['Id'],
            "deal_name": opp['Name'],
            "company_name": opp['Account']['Name'] if opp.get('Account') else "Unknown Account",
            "stage": opp['StageName'],
            "amount": clean_amount,
            "days_stalled": days_stalled,
            "rep_touchpoints": touchpoints,
            "client_engagement_index": client_engagement_index
        })

    print(f"[SALESFORCE] Successfully extracted all {len(ml_ready_data)} active Opportunities.")
    return pd.DataFrame(ml_ready_data)


def patch_pipeline(df: pd.DataFrame):
    """REVERSE ETL: Pushes the AI Flight Risk back to Salesforce Opportunities."""
    print("[SALESFORCE] Beginning surgical PATCH sequence...")
    sf = get_sf_connection()
    success_count = 0
    error_count = 0

    for _, row in df.iterrows():
        deal_id = row['crm_id']
        
        # CAST TO NATIVE PYTHON FLOAT to prevent Numpy JSON serialization errors
        flight_risk = float(row['calculated_flight_risk'])

        try:
            sf.Opportunity.update(deal_id, {"AI_Flight_Risk__c": flight_risk})
            success_count += 1
        except exceptions.SalesforceResourceNotFound:
            print(f"[SF ERROR] Opportunity ID {deal_id} not found in Salesforce.")
            error_count += 1
        except exceptions.SalesforceMalformedRequest as e:
            # EXPOSE THE ERROR: Print exactly why Salesforce rejected it (e.g., missing field)
            print(f"[SF ERROR] Malformed Request on Deal {deal_id}: {e}")
            error_count += 1
        except Exception as e:
            print(f"[NETWORK ERROR] Failed to patch Deal {deal_id}: {e}")
            error_count += 1
            
        time.sleep(0.05) # Concurrency safety

    print(f"[SALESFORCE] Sync Complete. Success: {success_count} | Errors: {error_count}")