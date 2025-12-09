# 🚦 Valencia Traffic Data Platform

A Data Engineering project to ingest, process, and analyze real-time traffic data from Valencia, Spain, creating a historical dataset for predictive modeling.

## 🏗 Architecture

1.  **Ingestion (The Chronicler):** Fetches real-time data from Valencia Open Data API every 10 minutes.
2.  **Storage (Data Lake):** Stores raw JSON snapshots partitioned by date.
3.  **Processing (The Refiner):** (Planned) dbt + BigQuery to clean and model history.
4.  **Analysis (The Oracle):** (Planned) Machine Learning model to predict traffic congestion.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+

### Setup
1.  Clone the repository.
2.  Install dependencies (none yet, standard library used for now, `requests` needed later).
    ```bash
    pip install requests
    ```
3.  Run the ingestion script:
    ```bash
    python src/ingestion/ingest_traffic.py
    ```

## 📂 Data Source
- **API:** [Valencia Open Data - Estado Tráfico Tiempo Real](https://valencia.opendatasoft.com/explore/dataset/estat-transit-temps-real-estado-trafico-tiempo-real/api/)
- **Update Frequency:** Every 3 minutes (Source). We ingest every 10 minutes.
