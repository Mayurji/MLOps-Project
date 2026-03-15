from feast import FeatureStore
import pandas as pd
from datetime import datetime

# Initialize the feature store
store = FeatureStore(repo_path="/home/mayur/Documents/MLOps-Project/real-time-fraud-detection/feature_repo")

def get_online_features(user_id):
    # Features we want to retrieve
    feature_names = [
        "transaction_features:amount",
        "transaction_features:transaction_time",
        "transaction_features:user_age",
        "transaction_features:is_international",
        "transaction_features:avg_30d_spending",
    ]
    
    # Entity rows for which we want to get features
    entity_rows = [{"user_id": user_id}]
    
    # Get online features
    features = store.get_online_features(
        features=feature_names,
        entity_rows=entity_rows,
    ).to_dict()
    
    return features

if __name__ == "__main__":
    # Example user_id from the dummy data
    user_id = 11
    
    print(f"Retrieving online features for user_id: {user_id}...")
    features = get_online_features(user_id)
    
    # Display the results
    print("\nOnline Features retrieved from Redis:")
    for key, value in features.items():
        print(f"{key}: {value}")
