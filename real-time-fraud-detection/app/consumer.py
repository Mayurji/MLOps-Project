import json
import joblib
import numpy as np
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

model = joblib.load("model/fraud_model.pkl")

def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                "transactions",
                bootstrap_servers="kafka:9092",
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="fraud-group"
            )
            print("Consumer connected.")
            return consumer
        except NoBrokersAvailable:
            print("Waiting for Kafka...")
            time.sleep(1)

consumer = create_consumer()

for message in consumer:
    txn = message.value

    features = np.array([[
        txn["amount"],
        txn["transaction_time"],
        txn["user_age"],
        txn["is_international"]
    ]])

    prediction = model.predict(features)[0]

    if prediction == 1:
        print("🚨 FRAUD:", txn)
    else:
        print("✅ Legit:", txn)