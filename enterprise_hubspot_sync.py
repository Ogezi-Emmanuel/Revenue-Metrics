import os
import time
import requests
import pandas as pd
import re
from dotenv import load_dotenv

# Load credentials
load_dotenv()
HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def clean_domain(company_name: str) -> str:
    """Converts a company name into a clean email domain (e.g., 'Acme Corp' -> 'acmecorp.com')."""
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name).lower()
    return f"{clean_name[:12]}.com"

def execute_request_with_backoff(method, url, payload=None, max_retries=3):
    """A bulletproof wrapper that handles HubSpot's 429 Rate Limits automatically."""
    for attempt in range(max_retries):
        if method == 'POST':
            response = requests.post(url, headers=HEADERS, json=payload)
        elif method == 'PUT':
            response = requests.put(url, headers=HEADERS)
            
        if response.status_code in [200, 201]:
            return True, response.json()
        elif response.status_code == 429:
            sleep_time = (2 ** attempt) + 1
            print(f"    [!] Rate Limit Hit. Backing off {sleep_time}s...")
            time.sleep(sleep_time)
        else:
            print(f"    [X] API Error {response.status_code}: {response.text}")
            return False, None
    return False, None

def relational_sync_pipeline(row: pd.Series):
    """
    Executes the 4-step relational database binding for a single record.
    """
    company_name = row['company_name']
    domain = clean_domain(company_name)
    
    # ---------------------------------------------------------
    # STEP 1: CREATE COMPANY
    # ---------------------------------------------------------
    comp_payload = {"properties": {"name": company_name, "domain": domain}}
    comp_success, comp_data = execute_request_with_backoff('POST', "https://api.hubapi.com/crm/v3/objects/companies", comp_payload)
    if not comp_success: return False
    company_id = comp_data['id']

    # ---------------------------------------------------------
    # STEP 2: CREATE CONTACT
    # ---------------------------------------------------------
    cont_payload = {"properties": {"email": f"director@{domain}", "firstname": "System", "lastname": "Contact"}}
    cont_success, cont_data = execute_request_with_backoff('POST', "https://api.hubapi.com/crm/v3/objects/contacts", cont_payload)
    if not cont_success: return False
    contact_id = cont_data['id']

    # ---------------------------------------------------------
    # STEP 3: CREATE DEAL (WITH INLINE ASSOCIATIONS)
    # HubSpot v3 allows binding IDs during the Deal creation payload!
    # Association Types: Deal to Contact = 3, Deal to Company = 5
    # ---------------------------------------------------------
    deal_payload = {
        "properties": {
            "dealname": row['deal_name'],
            "amount": str(row['amount']),
            "dealstage": row['stage'],
            "days_stalled_custom": str(row['days_stalled']),
            "engagement_index_custom": str(row['client_engagement_index'])
        },
        "associations": [
            {
                "to": {"id": company_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}]
            },
            {
                "to": {"id": contact_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}]
            }
        ]
    }
    
    deal_success, deal_data = execute_request_with_backoff('POST', "https://api.hubapi.com/crm/v3/objects/deals", deal_payload)
    
    if deal_success:
        return True
    return False


if __name__ == "__main__":
    print("=== INITIALIZING ENTERPRISE MULTI-OBJECT SYNC ===")
    
    try:
        df = pd.read_csv("synthetic_pipeline_payload.csv")
    except FileNotFoundError:
        print("CRITICAL: synthetic_pipeline_payload.csv not found.")
        exit()

    success_count = 0
    total_records = len(df)
    
    for index, row in df.iterrows():
        print(f"[{index + 1}/{total_records}] Syncing Relational Tree for: {row['company_name']}...")
        
        success = relational_sync_pipeline(row)
        if success:
            success_count += 1
            
        # THROTTLE: 3 requests per row. We need to stay under 100 requests per 10 seconds.
        # Sleeping for 0.35 seconds guarantees we max out at ~8 requests per second.
        time.sleep(0.35)

    print("\n=== PIPELINE EXECUTION COMPLETE ===")
    print(f"Successfully constructed {success_count} fully relational B2B SaaS Deal Trees.")