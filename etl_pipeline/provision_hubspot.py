import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_PRIVATE_TOKEN = os.getenv("HUBSPOT_PRIVATE_TOKEN")

def provision_hubspot_schema():
    print("=== PROVISIONING HUBSPOT SCHEMA ===")
    url = "https://api.hubapi.com/crm/v3/properties/deals"
    
    headers = {
        "Authorization": f"Bearer {HUBSPOT_PRIVATE_TOKEN}",
        "Content-Type": "application/json"
    }

    # The exact schema definition your script is looking for
    payload = {
        "name": "ai_flight_risk",
        "label": "AI Flight Risk",
        "type": "number",
        "fieldType": "number",
        "groupName": "dealinformation", 
        "description": "Calculated by the RevOps AI Inference Engine",
        "hidden": False
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("[SUCCESS] Column 'ai_flight_risk' created successfully.")
    elif response.status_code == 409:
        print("[SKIPPED] Column 'ai_flight_risk' already exists.")
    else:
        print(f"[ERROR] Failed to create column: {response.text}")

if __name__ == "__main__":
    provision_hubspot_schema()