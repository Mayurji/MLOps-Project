import json
import time
import requests
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import os

kafka_broker = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
simulator_url = os.getenv("SIMULATOR_URL", "http://api:8000/generate")

def create_producer():
    """ Creates a Kafka producer
    """
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_broker,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print(f"Connected to Kafka at {kafka_broker}.")
            return producer
        except NoBrokersAvailable:
            print(f"Waiting for Kafka at {kafka_broker}...")
            time.sleep(5)

producer = create_producer()

def fetch_transaction():
    try:
        response = requests.get(simulator_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from simulator: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to connect to simulator: {e}")
        return None

while True:
    txn = fetch_transaction()
    if txn:
        producer.send("transactions", txn)
        print("Sent:", txn)
    time.sleep(1)