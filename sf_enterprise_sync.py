import os
import pandas as pd
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load credentials
load_dotenv()
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_TOKEN = os.getenv("SF_SECURITY_TOKEN")

def run_salesforce_ingestion(csv_path: str, record_limit: int = 400):
    print("Authenticating with Salesforce Enterprise...")
    
    try:
        sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token=SF_TOKEN)
    except Exception as e:
        print(f"CRITICAL: Authentication failed. {e}")
        return

    try:
        # Slice the dataframe to prevent the 5MB Storage Crash
        df = pd.read_csv(csv_path).head(record_limit)
    except FileNotFoundError:
        print("CRITICAL: CSV payload not found.")
        return
        
    # Salesforce strictly requires a CloseDate for all Opportunities
    close_date_str = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    success_count = 0
    
    print(f"Starting Relational Sync for {record_limit} deal trees into Salesforce...\n")
    
    for index, row in df.iterrows():
        company_name = row['company_name']
        print(f"[{index + 1}/{record_limit}] Constructing tree for: {company_name}")
        
        try:
            # ---------------------------------------------------------
            # STEP 1: CREATE ACCOUNT (Company)
            # ---------------------------------------------------------
            account_res = sf.Account.create({'Name': company_name})
            account_id = account_res.get('id')
            
            # ---------------------------------------------------------
            # STEP 2: CREATE CONTACT
            # ---------------------------------------------------------
            domain = company_name.replace(" ", "").replace(",", "").lower()[:10] + ".com"
            sf.Contact.create({
                'FirstName': 'System',
                'LastName': 'Contact',
                'Email': f"director@{domain}",
                'AccountId': account_id
            })
            
            # ---------------------------------------------------------
            # STEP 3: CREATE OPPORTUNITY (Deal)
            # ---------------------------------------------------------
            # Map the ML telemetry to the Description field
            description_payload = f"AI_TELEMETRY | Days Stalled: {row['days_stalled']} | Engagement Index: {row['client_engagement_index']}"
            
            # Map HubSpot stages to standard Salesforce stages
            sf_stage = "Prospecting"
            if row['stage'] == 'closedwon': sf_stage = "Closed Won"
            elif row['stage'] == 'closedlost': sf_stage = "Closed Lost"
            elif row['stage'] == 'contractsent': sf_stage = "Negotiation/Review"
            elif row['stage'] == 'presentationscheduled': sf_stage = "Value Proposition"
            
            sf.Opportunity.create({
                'Name': row['deal_name'],
                'Amount': row['amount'],
                'StageName': sf_stage,
                'CloseDate': close_date_str,
                'AccountId': account_id,
                'Description': description_payload
            })
            
            success_count += 1
            
        except Exception as e:
            print(f"  [X] Failed on {company_name}: {str(e)}")
            
    print("\n=== SALESFORCE PIPELINE COMPLETE ===")
    print(f"Successfully injected {success_count} enterprise deal trees.")

if __name__ == "__main__":
    run_salesforce_ingestion("synthetic_pipeline_payload.csv")