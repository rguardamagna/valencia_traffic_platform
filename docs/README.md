# 🚦 Valencia Traffic Data Platform

A Data Engineering project to ingest, process, and analyze real-time traffic data from Valencia, Spain, creating a historical dataset for predictive modeling.

## 🏗 Architecture

1.  **Ingestion ("The Chronicler"):** Fetches real-time data from Valencia Open Data API every 10 minutes. Handles API pagination to retrieve all ~400 sensors.
2.  **Storage (Data Lake):** Stores raw JSON snapshots partitioned by date (`data/raw/YYYY/MM/DD/`).
3.  **Exploration ("The Refiner"):** Jupyter Lab instance running on the VPS for direct analysis of the Data Lake.
4.  **Processing & Analysis ("The Oracle"):** Machine Learning model (XGBoost) to predict traffic congestion. Validated with 88% Recall.
5.  **Visualization ("The Spotlight"):** Streamlit dashboard providing real-time maps and system health metrics.

## 🚀 Project Status
- **Status:** 🟢 Dashboard Operativo (Local/Dev) | 🟢 Ingestión en Producción (VPS).
- **Last Update:** 26/12/2025
- **Current Milestone:** "The Spotlight" (Streamlit Dashboard) lanzado. Modelo "The Oracle" integrado y listo para inferencia.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose

### Setup (VPS or Local with Docker)

1.  **Clone the repository.**
2.  **Environment Setup:**
    Create a `.env` file in the root directory (or use `.env.example` as a template):
    ```bash
    # Set your user ID for permission management
    echo "AIRFLOW_UID=$(id -u)" > .env
    
    # Optional: Configure API URL and Data Directory
    # echo "VALENCIA_TRAFFIC_API_URL=https://..." >> .env
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

## 🛠️ Configuration & Portability
- **Configuration:** API URL and other settings are managed via environment variables and `os.environ`.
- **Paths:** The project uses `pathlib` for robust path handling.
- **Airflow Variables:** Use `valencia_traffic_data_path` in Airflow UI to configure where data is stored on the host (Default: `/opt/valencia_traffic_platform/data` or `/root/valencia_traffic_platform/data`).
