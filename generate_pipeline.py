import pandas as pd
import numpy as np
from faker import Faker

# Instantiate Faker and set static seeds so your portfolio data is reproducible
fake = Faker()
Faker.seed(42)
np.random.seed(42)

def generate_saas_deals(num_records=3000):
    print(f"Initializing generation of {num_records} synthetic B2B SaaS opportunities...")
    
    # 1. Generate Realistic Tech Company Names
    companies = [fake.unique.company() for _ in range(num_records)]

    # 2. Deal Types (70% New Logos, 30% Account Expansion)
    deal_types = np.random.choice(
        ['newbusiness', 'existingbusiness'], 
        size=num_records, 
        p=[0.7, 0.3]
    )

    # 3. SaaS ARR Amounts (Log-normal distribution: mostly $10k-$50k, with a few $200k+ whales)
    log_amounts = np.random.lognormal(mean=10.3, sigma=0.8, size=num_records)
    amounts = np.round(log_amounts, -2) # Round to nearest $100
    amounts = np.clip(amounts, 5000, 350000).astype(int)

    # 4. HubSpot Internal Pipeline Stages
    stages = np.random.choice(
        [
            'appointmentscheduled', 
            'qualifiedtobuy', 
            'presentationscheduled', 
            'decisionmakerboughtin', 
            'contractsent', 
            'closedwon', 
            'closedlost'
        ],
        size=num_records,
        p=[0.20, 0.20, 0.15, 0.10, 0.05, 0.20, 0.10]
    )

    # 5. Assigned Account Executives (Sales Reps)
    reps = np.random.choice(
        ['Sarah Jenkins', 'Marcus Vance', 'Elena Rostova', 'David Chen', 'Rachel Zane'],
        size=num_records
    )

    # ==========================================
    # 6. THE TELEMETRY (Your Machine Learning Features)
    # ==========================================
    
    # Days the deal has been sitting in its current stage without moving
    days_stalled = np.random.exponential(scale=14, size=num_records).astype(int)
    
    # Number of times the sales rep logged a call or email
    rep_touchpoints = np.random.poisson(lam=5, size=num_records).astype(int)

    # Client Engagement Index (0.00 to 1.00)
    engagement = np.random.normal(loc=0.7, scale=0.2, size=num_records)
    
    # Business Logic Gate: If a deal is lost or heavily stalled, penalize its engagement score
    stalled_mask = (stages == 'closedlost') | (days_stalled > 25)
    engagement[stalled_mask] = engagement[stalled_mask] * 0.35
    engagement = np.clip(engagement, 0.05, 1.0)

    # Build DataFrame
    df = pd.DataFrame({
        'deal_name': [f"{comp} - Q3 License" for comp in companies],
        'company_name': companies,
        'deal_type': deal_types,
        'amount': amounts,
        'stage': stages,
        'sales_owner': reps,
        'days_stalled': days_stalled,
        'rep_touchpoints': rep_touchpoints,
        'client_engagement_index': np.round(engagement, 2)
    })

    return df

if __name__ == "__main__":
    pipeline_df = generate_saas_deals(3000)
    
    # Law of Data Engineering: Always commit a local static backup before API ingestion
    output_filename = "synthetic_pipeline_payload.csv"
    pipeline_df.to_csv(output_filename, index=False)
    
    print(f"\nSUCCESS: Dataset compiled and saved to '{output_filename}'.")
    print("\nPayload Architecture Preview:")
    print(pipeline_df[['deal_name', 'amount', 'stage', 'days_stalled', 'client_engagement_index']].head(5))