import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_dummy_data(output_path):
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Number of users and records
    num_users = 100
    num_records = 1000
    
    user_ids = np.arange(1, num_users + 1)
    
    data = {
        "user_id": np.random.choice(user_ids, num_records),
        "amount": np.random.uniform(10.0, 5000.0, num_records),
        "transaction_time": np.random.uniform(0.0, 24.0, num_records), # Hour of day
        "user_age": np.random.randint(18, 80, num_records),
        "is_international": np.random.choice([0, 1], num_records, p=[0.9, 0.1]),
        "avg_30d_spending": np.random.uniform(100.0, 10000.0, num_records), # Pre-calculated aggregate
        "event_timestamp": [datetime.now() - timedelta(minutes=np.random.randint(0, 1440)) for _ in range(num_records)],
    }
    
    df = pd.DataFrame(data)
    
    # Sort by timestamp for Feast
    df = df.sort_values("event_timestamp")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to Parquet
    df.to_parquet(output_path)
    print(f"Dummy data generated at {output_path}")
    print(df.head())

if __name__ == "__main__":
    path = "/home/mayur/Documents/MLOps-Project/real-time-fraud-detection/feature_repo/data/transactions.parquet"
    generate_dummy_data(path)
