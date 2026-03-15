import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
import mlflow
from sklearn.metrics import accuracy_score, precision_score, recall_score

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("FraudDetection")

print(mlflow.get_tracking_uri())

parquet_path = "/home/mayur/Documents/MLOps-Project/real-time-fraud-detection/feature_repo/data/transactions.parquet"

def load_data_from_parquet():
    """ Loads transaction data from the Feast offline store (parquet)
    """
    if not os.path.exists(parquet_path):
        # Fallback to creating dummy data if parquet doesn't exist (though it should)
        print(f"Warning: {parquet_path} not found. Running generate_data.py first might be needed.")
        return pd.DataFrame()
    
    df = pd.read_parquet(parquet_path)
    
    # Create synthetic target 'fraud' for demonstration
    # Logic: high amount + international OR abnormally high amount compared to 30d average
    df["fraud"] = (
        ((df["amount"] > 4000) & (df["is_international"] == 1)) |
        (df["amount"] > (df["avg_30d_spending"] * 2.0))
    ).astype(int)
    
    print(f"Loaded {len(df)} records from {parquet_path}")
    print(f"Fraud distribution: {df['fraud'].value_counts().to_dict()}")
    
    return df

def train():
    df = load_data_from_parquet()
    if df.empty:
        return

    # Features used for training
    features = ["amount", "transaction_time", "user_age", "is_international", "avg_30d_spending"]
    X = df[features]
    y = df["fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    # Calculate metrics with zero_division parameter safety
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)

    print(f"Metrics - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")

    # MLflow logging
    try:
        with mlflow.start_run():
            mlflow.log_param("n_estimators", 100)
            mlflow.log_param("random_state", 42)
            mlflow.log_param("features", features)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            
            # Log the model and register it
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="fraud_model",
                registered_model_name="fraud_model"
            )
            print("Model logged and registered in MLflow.")
    except Exception as e:
        print(f"MLflow logging failed: {e}. Check if MLflow server is reachable at {mlflow_uri}")

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/fraud_model.pkl")
    print("Model trained and saved locally as well.")

if __name__ == "__main__":
    train()