import json
import numpy as np
import time
import mlflow.sklearn
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from feast import FeatureStore
import os

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
kafka_broker = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
feast_repo_path = os.getenv("FEAST_REPO_PATH", "/feature_repo")

mlflow.set_tracking_uri(mlflow_uri)
# Load the latest version of the model from the registry (with retry)
model_name = "fraud_model"
model_version = "latest"
model = None

print(f"Waiting for model '{model_name}' to be available in registry...")
while model is None:
    try:
        model = mlflow.sklearn.load_model(f"models:/{model_name}/{model_version}")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Model not found yet, retrying in 10s... ({e})")
        time.sleep(10)

# Initialize Feast Feature Store
store = FeatureStore(repo_path=feast_repo_path)

def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                "transactions",
                bootstrap_servers=kafka_broker,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest", # start from beginning
                enable_auto_commit=True, # commit automatically
                group_id="fraud-group" # group of consumers
            )
            print("Consumer connected.")
            return consumer
        except NoBrokersAvailable:
            print("Waiting for Kafka...")
            time.sleep(1)

consumer = create_consumer()

for message in consumer:
    txn = message.value
    user_id = txn.get("user_id")
    
    # Fetch avg_30d_spending from Feast (Redis)
    print(f"Fetching features for user_id: {user_id}")
    try:
        feature_vector = store.get_online_features(
            features=["transaction_features:avg_30d_spending"],
            entity_rows=[{"user_id": user_id}]
        ).to_dict()
        print(f"Full feature vector for {user_id}: {feature_vector}")
        
        # Feast to_dict() returns a dict with lists as values
        avg_30d_spending = feature_vector.get("avg_30d_spending", [0.0])[0]
        # Sometimes Feast returns the feature name as is, or with the feature view name prefix
        if avg_30d_spending is None:
             avg_30d_spending = feature_vector.get("transaction_features:avg_30d_spending", [0.0])[0]
             
        if avg_30d_spending is None:
            avg_30d_spending = 0.0
            
    except Exception as e:
        print(f"Error fetching features from Feast: {e}")
        avg_30d_spending = 0.0

    print(f"Joined avg_30d_spending: {avg_30d_spending}")

    # Join features: 4 from Kafka + 1 from Feast
    features = np.array([[
        txn["amount"],
        txn["transaction_time"],
        txn["user_age"],
        txn["is_international"],
        avg_30d_spending
    ]])

    prediction = model.predict(features)[0]

    if prediction == 1:
        print(f"🚨 FRAUD DETECTED | User: {user_id} | Amount: {txn['amount']} | Avg Spend: {avg_30d_spending}")
    else:
        print(f"✅ Legit Transaction | User: {user_id} | Amount: {txn['amount']}")