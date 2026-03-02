from fastapi import FastAPI
import joblib
import numpy as np
from pydantic import BaseModel

app = FastAPI()
model = joblib.load("model/fraud_model.pkl")

class Transaction(BaseModel):
    amount: float
    transaction_time: float
    user_age: int
    is_international: int

@app.post("/predict")
def predict(txn: Transaction):
    features = np.array([[
        txn.amount,
        txn.transaction_time,
        txn.user_age,
        txn.is_international
    ]])

    prediction = model.predict(features)[0]

    return {"fraud_prediction": int(prediction)}