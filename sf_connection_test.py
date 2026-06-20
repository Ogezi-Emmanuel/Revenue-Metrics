import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_TOKEN = os.getenv("SF_SECURITY_TOKEN")

def test_salesforce_connection():
    print("Initiating authentication handshake with Salesforce...")
    
    try:
        # Initialize the connection
        sf = Salesforce(
            username=SF_USERNAME, 
            password=SF_PASSWORD, 
            security_token=SF_TOKEN
        )
        print("SUCCESS: Authenticated into Salesforce Enterprise.\n")
        
        # Write a basic SOQL query to target the Revenue Object (Opportunity)
        query = "SELECT Id, Name, Amount, StageName FROM Opportunity LIMIT 5"
        print(f"Executing SOQL Query: {query}\n")
        
        # Execute the query
        response = sf.query(query)
        
        print("=== SALESFORCE PIPELINE DATA ===")
        for record in response.get('records', []):
            # Salesforce returns an 'attributes' dictionary in each record we can ignore
            print(f"Opportunity: {record.get('Name')}")
            print(f"Amount:      ${record.get('Amount')}")
            print(f"Stage:       {record.get('StageName')}")
            print("-" * 40)
            
    except Exception as e:
        print("CRITICAL ERROR: Connection Failed.")
        print(e)

if __name__ == "__main__":
    test_salesforce_connection()