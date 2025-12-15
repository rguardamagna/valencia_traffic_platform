# 🚦 Valencia Traffic Data Platform

A Data Engineering project to ingest, process, and analyze real-time traffic data from Valencia, Spain, creating a historical dataset for predictive modeling.

## 🏗 Architecture

1.  **Ingestion (The Chronicler):** Fetches real-time data from Valencia Open Data API every 10 minutes.
2.  **Storage (Data Lake):** Stores raw JSON snapshots partitioned by date.
3.  **Processing (The Refiner):** (Planned) dbt + BigQuery to clean and model history.
4.  **Analysis (The Oracle):** (Planned) Machine Learning model to predict traffic congestion.

## 🚀 Project Status
- **Status:** 🟢 In Production (Ingestion Active)
- **Last Update:** 11/12/2025
- **Current Milestone:** Real-time traffic data ingestion operational on VPS.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+

### Setup
### Setup (VPS or Local with Docker)

1.  **Clone the repository.**
2.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```bash
    echo "AIRFLOW_UID=50000" > .env
    ```
3.  **Build Ingestion Image:**
    This image is used by Airflow's DockerOperator.
    ```bash
    docker compose build ingestion-build
    ```
4.  **Start Platform:**
    Initialize Airflow and start services.
    ```bash
    docker compose up airflow-init
    docker compose up -d
    ```
5.  **Access Airflow:**
    - URL: `http://localhost:8080` (or `http://your-vps-ip:8080`)
    - User: `airflow`
    - Password: `airflow`
6.  **Trigger Ingestion:**
    Enable the `valencia_traffic_ingestion` DAG in the UI.

## 🔐 Security & Users
- **Default Credentials:** The default user is `airflow` / `airflow`.
- **Important:** The `_AIRFLOW_WWW_USER_PASSWORD` defined in `.env` is **only used during the first initialization**.
- **Changing Password:** If the user already exists, changing `.env` will have **no effect**. To change the password manually:
  ```bash
  docker-compose exec airflow-webserver airflow users reset-password --username airflow --password "NEW_PASSWORD"
  ```

## 📂 Data Source
- **API:** [Valencia Open Data - Estado Tráfico Tiempo Real](https://valencia.opendatasoft.com/explore/dataset/estat-transit-temps-real-estado-trafico-tiempo-real/api/)
- **Update Frequency:** Every 3 minutes (Source). We ingest every 10 minutes.
