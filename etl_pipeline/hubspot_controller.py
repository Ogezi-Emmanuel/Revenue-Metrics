import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_PRIVATE_TOKEN = os.getenv("HUBSPOT_PRIVATE_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_PRIVATE_TOKEN}",
    "Content-Type": "application/json"
}

def extract_pipeline():
    """FORWARD ETL: Pulls live HubSpot deals using pagination and applies ML heuristic formatting."""
    print("[HUBSPOT] Querying active pipeline...")
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    
    # Base payload without the "after" pagination token
    base_payload = {
        "filterGroups": [{"filters": [{"propertyName": "dealstage", "operator": "NOT_IN", "values": ["closedwon", "closedlost"]}]}],
        "properties": ["dealname", "amount", "dealstage", "hs_time_in_stage", "num_contacted_notes"],
        "limit": 100
    }

    deals_data = []
    has_more = True
    after_token = None

    # --- THE PAGINATION LOOP ---
    while has_more:
        # Attach the bookmark token if we have one
        if after_token:
            base_payload["after"] = after_token
            
        response = requests.post(url, headers=HEADERS, json=base_payload)
        response.raise_for_status()
        
        json_data = response.json()
        
        # Add this batch of 100 to our master list
        deals_data.extend(json_data.get('results', []))
        
        # Check if HubSpot gave us a bookmark for the next page
        if 'paging' in json_data and 'next' in json_data['paging']:
            after_token = json_data['paging']['next']['after']
            print(f"Fetched {len(deals_data)} deals... turning page...")
        else:
            has_more = False # End of database reached

    # --- DATA TRANSFORMATION ---
    # --- DATA TRANSFORMATION ---
    ml_ready_data = []
    for deal in deals_data:
        props = deal.get('properties', {})
        
        # 1. Parse the Deal Name to extract the Company
        raw_deal_name = props.get('dealname', 'Unnamed Deal')
        
        # Split by hyphen. "Acme Corp - Q3 License" becomes ["Acme Corp", "Q3 License"]
        if ' - ' in raw_deal_name:
            company_name = raw_deal_name.split(' - ')[0].strip()
        elif '-' in raw_deal_name:
            company_name = raw_deal_name.split('-')[0].strip()
        else:
            company_name = raw_deal_name # Fallback if no hyphen exists

        # Financials
        raw_amount = props.get('amount')
        clean_amount = float(raw_amount) if raw_amount and str(raw_amount).strip() else 0.0

        # Days Stalled (Convert ms to days)
        ms_stalled = props.get('hs_time_in_stage')
        try:
            ms_val = int(ms_stalled) if ms_stalled else 0
            days_stalled = int(ms_val / (1000 * 60 * 60 * 24)) if ms_val > 0 else 1
        except (ValueError, TypeError):
            days_stalled = 1

        # Heuristic Engagement Algorithm
        raw_touchpoints = props.get('num_contacted_notes')
        try:
            touchpoints = int(raw_touchpoints) if raw_touchpoints is not None else 0
        except (ValueError, TypeError):
            touchpoints = 0
            
        raw_engagement = 5.0 + (touchpoints * 0.5) - (days_stalled * 0.2)
        client_engagement_index = max(1.0, min(10.0, round(raw_engagement, 1))) / 10.0

        ml_ready_data.append({
            "crm_id": deal.get('id'),
            "deal_name": raw_deal_name,
            "company_name": company_name,  # <--- Now dynamically extracted!
            "stage": props.get('dealstage', 'unknown'),
            "amount": clean_amount,
            "days_stalled": days_stalled,     
            "rep_touchpoints": touchpoints, 
            "client_engagement_index": client_engagement_index
        })

    print(f"[HUBSPOT] Successfully extracted all {len(ml_ready_data)} active deals.")
    return pd.DataFrame(ml_ready_data)


def patch_pipeline(df: pd.DataFrame):
    """REVERSE ETL: Pushes the AI Flight Risk back to HubSpot deals."""
    print("[HUBSPOT] Beginning surgical PATCH sequence...")
    success_count = 0
    error_count = 0

    for _, row in df.iterrows():
        deal_id = row['crm_id']
        
        # CAST TO NATIVE PYTHON FLOAT to prevent Numpy JSON serialization errors
        flight_risk = float(row['calculated_flight_risk'])
        
        url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
        payload = {"properties": {"ai_flight_risk": flight_risk}}

        try:
            res = requests.patch(url, headers=HEADERS, json=payload)
            if res.status_code == 200:
                success_count += 1
            elif res.status_code == 429:
                time.sleep(5) # Rate limit safety
            else:
                # EXPOSE THE ERROR: Print exactly why HubSpot rejected it
                print(f"[HUBSPOT ERROR] Deal {deal_id} Failed: HTTP {res.status_code} - {res.text}")
                error_count += 1
        except Exception as e:
            print(f"[NETWORK ERROR] Failed to patch Deal {deal_id}: {e}")
            error_count += 1
            
        time.sleep(0.05) # Concurrency safety

    print(f"[HUBSPOT] Sync Complete. Success: {success_count} | Errors: {error_count}")