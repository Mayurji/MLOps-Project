import json
import time
import random
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def create_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers="0.0.0.0:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("Connected to Kafka.")
            return producer
        except NoBrokersAvailable:
            print("Waiting for Kafka...")
            time.sleep(1)

producer = create_producer()

def generate_transaction():
    return {
        "amount": random.uniform(10, 1000),
        "transaction_time": random.uniform(0, 24),
        "user_age": random.randint(18, 70),
        "is_international": random.randint(0, 1)
    }

while True:
    txn = generate_transaction()
    producer.send("transactions", txn)
    print("Sent:", txn)
    time.sleep(1)