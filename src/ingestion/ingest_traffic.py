import requests
import json
import os
from datetime import datetime
import logging

# Configuration
API_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estat-transit-temps-real-estado-trafico-tiempo-real/records?limit=-1"
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "raw")

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_traffic_data():
    """Fetches real-time traffic data from Valencia Open Data API."""
    try:
        logging.info("Fetching data from API...")
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Successfully fetched {data.get('total_count', 'unknown')} records.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return None

def save_data(data):
    """Saves data to a JSON file with a timestamp-based folder structure."""
    if not data:
        return

    now = datetime.now()
    timestamp_str = now.isoformat()
    
    # Add ingestion metadata
    data['ingestion_metadata'] = {
        'ingestion_timestamp': timestamp_str,
        'source_url': API_URL
    }

    # Define path: data/raw/YYYY/MM/DD/traffic_HHMMSS.json
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    filename = f"traffic_{now.strftime('%H%M%S')}.json"

    target_dir = os.path.join(BASE_DATA_DIR, year, month, day)
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, filename)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Data saved to {file_path}")
    except IOError as e:
        logging.error(f"Error saving file: {e}")

if __name__ == "__main__":
    logging.info("Starting ingestion job...")
    traffic_data = fetch_traffic_data()
    save_data(traffic_data)
    logging.info("Ingestion job finished.")
