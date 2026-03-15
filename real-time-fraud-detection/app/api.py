from fastapi import FastAPI
import numpy as np
import mlflow.sklearn
from pydantic import BaseModel
import os
import time
import mlflow.pyfunc
import random

app = FastAPI()

mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(mlflow_uri)

# Load the latest version of the model from the registry (with retry)
model_name = "fraud_model"
model_version = "latest" 
model = None

print(f"Waiting for model '{model_name}' to be available in registry...")
while model is None:
    try:
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Model not found yet, retrying in 10s... ({e})")
        time.sleep(10)

class Transaction(BaseModel):
    """ Transaction class: schema validation for the transaction data
    """
    user_id: int
    amount: float
    transaction_time: float
    user_age: int
    is_international: int

@app.post("/predict")
def predict(txn: Transaction):
    """ Predicts the fraud probability for a given transaction
    """
    # Note: This endpoint should also fetch avg_30d_spending if it were to be used for real predictions
    # but the task focuses on the consumer joining these features.
    features = np.array([[
        txn.amount,
        txn.transaction_time,
        txn.user_age,
        txn.is_international,
        0.0  # Placeholder if not fetched from Feast here
    ]])

    prediction = model.predict(features)[0]

    return {"fraud_prediction": int(prediction)}

@app.get("/generate", response_model=Transaction)
async def generate_transaction():
    """Generates a random transaction."""
    
    print("Generating transaction...")

    txn = {
        "user_id": random.randint(1, 100),
        "amount": round(random.uniform(10, 1000), 2),
        "transaction_time": round(random.uniform(0, 24), 2),
        "user_age": random.randint(18, 70),
        "is_international": random.randint(0, 1)
    }

    print(f"Generated transaction: {txn}")

    return txn

if __name__ == "__main__":
    """ Runs the FastAPI server
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)