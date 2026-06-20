import os
import requests
from dotenv import load_dotenv

# Load the token securely
load_dotenv()
HUBSPOT_TOKEN = os.getenv("HUBSPOT_PRIVATE_TOKEN")

def test_hubspot_extraction():
    """
    Executes a GET request to the HubSpot Deals API.
    """
    url = "https://api.hubapi.com/crm/v3/objects/deals"
    
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # We want to extract specific pipeline properties
    params = {
        "limit": 5,
        "properties": ["dealname", "amount", "dealstage"]
    }

    print("Initiating GET request to HubSpot API...")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== SUCCESS: HUBSPOT PIPELINE DATA EXTRACTED ===")
        for deal in data.get('results', []):
            props = deal.get('properties', {})
            print(f"Deal Name: {props.get('dealname')}")
            print(f"Amount:    ${props.get('amount')}")
            print(f"Stage:     {props.get('dealstage')}")
            print("-" * 40)
    else:
        print(f"CRITICAL ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_hubspot_extraction()