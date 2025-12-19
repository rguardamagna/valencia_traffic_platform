import requests
import json
import os
from datetime import datetime
import logging
from pathlib import Path

# Configuration
# Definimos la raíz del proyecto de forma limpia con pathlib
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Inyeccion de variables de entorno con valores por defecto (Defensive Programming)
BASE_API_URL = os.environ.get("VALENCIA_TRAFFIC_API_URL")
if not BASE_API_URL:
    # Si no hay variable, usamos la de Opendatasoft por defecto para que el script no falle al descargarlo
    BASE_API_URL = "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estat-transit-temps-real-estado-trafico-tiempo-real/records"

# Usamos BASE_DIR para construir el path de datos de forma legible
env_data_dir = os.environ.get("VALENCIA_TRAFFIC_DATA_DIR")
BASE_DATA_DIR = Path(env_data_dir) if env_data_dir else BASE_DIR / "data" / "raw"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_traffic_data():
    """Fetches ALL real-time traffic data from Valencia Open Data API using pagination."""
    all_records = []
    offset = 0
    limit = 100 # Max limit per request for Opendatasoft v2.1
    
    try:
        logging.info("Fetching data from API with pagination...")
        
        while True:
            url = f"{BASE_API_URL}?limit={limit}&offset={offset}"
            logging.info(f"Requesting offset {offset}...")
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            records = data.get('results', [])
            if not records:
                break
                
            all_records.extend(records)
            
            total_count = data.get('total_count', 0)
            if len(all_records) >= total_count:
                break
                
            offset += limit

        logging.info(f"Successfully fetched {len(all_records)} records (Total available: {total_count}).")
        
        # Return structure compatible with previous logic but containing all results
        return {
            "total_count": total_count,
            "results": all_records,
            "ingestion_metadata": {} # Will be populated in save_data
        }
        
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
        'source_url': BASE_API_URL
    }

    # Define path: data/raw/YYYY/MM/DD/traffic_HHMMSS.json
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    filename = f"traffic_{now.strftime('%H%M%S')}.json"

    target_dir = BASE_DATA_DIR / year / month / day
    target_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = target_dir / filename

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
