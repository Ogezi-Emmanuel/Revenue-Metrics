import os
import requests
from dotenv import load_dotenv

# Load credentials
load_dotenv()
HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

def create_custom_deal_property(name: str, label: str, property_type: str, field_type: str):
    """
    Modifies the HubSpot database schema by creating a new custom property.
    """
    url = "https://api.hubapi.com/crm/v3/properties/deals"
    
    payload = {
        "name": name,
        "label": label,
        "type": property_type,
        "fieldType": field_type,
        "groupName": "dealinformation", # Default HubSpot group for deal data
        "hidden": False
    }

    print(f"Provisioning new database column: '{name}'...")
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        print(f"  -> SUCCESS: Schema updated with {name}.")
    elif response.status_code == 409:
        print(f"  -> SKIPPED: Property '{name}' already exists.")
    else:
        print(f"  -> ERROR {response.status_code}: {response.text}")

if __name__ == "__main__":
    print("=== INITIALIZING PIPELINE SCHEMA SETUP ===")
    
    # 1. Create the Days Stalled property (Number field)
    create_custom_deal_property(
        name="days_stalled_custom",
        label="Days Stalled (AI Custom)",
        property_type="number",
        field_type="number"
    )
    
    # 2. Create the Engagement Index property (Number field)
    create_custom_deal_property(
        name="engagement_index_custom",
        label="Client Engagement Index (AI Custom)",
        property_type="number",
        field_type="number"
    )
    
    print("\nSchema setup complete. You may now run the ingestion pipeline.")