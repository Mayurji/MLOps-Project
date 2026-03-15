# Understanding Kubernetes Deployment YAML: K8s Deployment

This file is a "blueprint" that tells Kubernetes exactly how to run your fraud detection system. It is divided into two main types of objects: **Deployments** and **Services**.

---

## 🏗️ Core Concepts

### 1. Deployment
Think of a **Deployment** as a "manager." It says: *"I want 1 copy of this specific Docker image running at all times."* If the container crashes, the Deployment automatically starts a new one.

### 2. Service
A **Service** is like a "static phone number." In Kubernetes, Pods (containers) get new IP addresses every time they restart. A Service gives them a permanent name (like `kafka` or `mlflow`) so other parts of your app can always find them.

---

## 🔍 Section-by-Section Breakdown

### 1. Kafka (The Message Broker)
Kafka works in **KRaft mode** (meaning it doesn't need Zookeeper).
- **Service**: Makes Kafka reachable at `kafka:9092`.
- **Environment Variables**:
    - `KAFKA_PROCESS_ROLES`: Tells this container to act as both the "storage" (broker) and the "manager" (controller).
    - `KAFKA_ADVERTISED_LISTENERS`: Tells other services where to find Kafka.
    - `KAFKA_CONTROLLER_QUORUM_VOTERS`: We set this to `localhost:9093` so Kafka can "talk to itself" internally to initialize the cluster.

### 2. MLflow (The Model Manager)
- **Deployment Flags**:
    - `--serve-artifacts`: This is the "magic bridge." It allows your training script (running on your laptop) to upload files into the container's storage.
    - `--artifacts-destination`: Tells MLflow where to store those files inside the container.
- **Volumes**: We use an `emptyDir` volume. This is a temporary folder that lives as long as the pod. (In a real bank, you'd use a "Persistent Volume" so your models don't disappear if the pod restarts).

### 3. FastAPI (The Prediction API)
- **Image**: `real-time-fraud-detection-api:latest`. This is the custom logic you built.
- **Environment Variables**: It uses `MLFLOW_TRACKING_URI: http://mlflow:5000` to find the MLflow service we created above.

### 4. Producer & Consumer
- **Producer**: A background worker that pushes fake transactions into Kafka.
- **Consumer**: A background worker that pulls data from Kafka, asks MLflow for the math model, and prints whether the transaction is "Legit" or "Fraud."
- **Note**: These don't have "Services" because they are internal workers; nothing needs to "call" them from the outside.

---

## 🏷️ The "Glue": Selectors and Labels
You'll notice `labels` and `matchLabels` everywhere.
- **Labels**: A tag we put on a Pod (e.g., `app: mlflow`).
- **Selector**: A filter the Service uses (e.g., *"Direct all traffic on port 5000 to any Pod tagged with `app: mlflow`."*)

---

## 🚀 How traffic flows
1. Your **Producer** sends data to → `kafka:9092`.
2. Your **Consumer** reads from → `kafka:9092`.
3. Your **Consumer** & **API** download models from → `mlflow:5000`.
4. **You** talk to the system via `port-forward` to `localhost:8000` or `5000`.
