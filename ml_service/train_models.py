import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
import joblib

def train_churn_classifier(df: pd.DataFrame):
    print("\n--- Training Churn Risk Classifier ---")
    
    # Isolate Terminal Stages
    terminal_df = df[df['stage'].isin(['closedwon', 'closedlost'])].copy()
    terminal_df['churn_target'] = terminal_df['stage'].apply(lambda x: 1 if x == 'closedlost' else 0)

    # Features & Target
    features = ['amount', 'days_stalled', 'rep_touchpoints', 'client_engagement_index']
    X = terminal_df[features]
    y = terminal_df['churn_target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Model (Balanced for Risk Sensitivity)
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    # Diagnostics
    preds = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, preds):.2%}")
    print("Classification Report:\n", classification_report(y_test, preds, target_names=['Won (0)', 'Lost (1)']))

    # Serialize
    joblib.dump(model, "revops_churn_model.joblib")
    print("SUCCESS: 'revops_churn_model.joblib' compiled.")


def train_velocity_regressor(df: pd.DataFrame):
    print("\n--- Training Sales Velocity Regressor ---")
    
    # Isolate Won Deals (You can only predict time-to-close on deals that actually closed)
    won_df = df[df['stage'] == 'closedwon'].copy()

    # Features & Target
    features = ['amount', 'rep_touchpoints', 'client_engagement_index']
    y = won_df['days_stalled']  # For won deals, 'days_stalled' equals the total sales cycle length
    X = won_df[features]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Model
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Diagnostics
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Mean Absolute Error (MAE): +/- {mae:.1f} Days")
    print(f"R-squared: {r2_score(y_test, preds):.2f}")

    # Serialize
    joblib.dump(model, "revops_velocity_regressor.joblib")
    print("SUCCESS: 'revops_velocity_regressor.joblib' compiled.")


if __name__ == "__main__":
    print("=== INITIATING DUAL-ENGINE AI COMPILATION ===")
    
    try:
        master_df = pd.read_csv("synthetic_pipeline_payload.csv")
        print(f"Ingested master dataset: {len(master_df)} records.")
    except FileNotFoundError:
        print("CRITICAL ERROR: 'synthetic_pipeline_payload.csv' not found. Run ETL pipeline first.")
        exit()

    # Run the merged pipeline
    train_churn_classifier(master_df)
    train_velocity_regressor(master_df)
    
    print("\n=== COMPILATION COMPLETE ===")