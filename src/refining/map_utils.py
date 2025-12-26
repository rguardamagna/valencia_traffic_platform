import json
import pandas as pd
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_sensor_geometries(sample_json_path: str):
    """
    Extracts sensor IDs and their corresponding geometry (Polylines) 
    from a sample JSON file to create a static master reference.
    
    Good Practice: Caching/Pre-processing. By extracting this once, 
    we avoid overhead in the real-time dashboard.
    """
    path = Path(sample_json_path)
    if not path.exists():
        logging.error(f"Sample file not found: {sample_json_path}")
        return pd.DataFrame()

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sensors = []
    if 'results' in data:
        for item in data['results']:
            # Folium and Leaflet expect [Lat, Lon]
            # GeoJSON usually provides [Lon, Lat]
            raw_coords = item.get('geo_shape', {}).get('geometry', {}).get('coordinates', [])
            
            # Valencia API might provide nested lists for polylines
            # We need to ensure we have a list of [Lat, Lon]
            clean_coords = []
            for coord in raw_coords:
                # Inversion: [Lon, Lat] -> [Lat, Lon]
                if len(coord) == 2:
                    clean_coords.append([coord[1], coord[0]])
            
            sensors.append({
                'idtramo': item.get('idtramo'),
                'denominacion': item.get('denominacion'),
                'coordinates': clean_coords
            })
            
    df_sensors = pd.DataFrame(sensors)
    logging.info(f"Extracted {len(df_sensors)} sensor geometries.")
    return df_sensors

def save_sensor_master(df, output_path: str = "data/sensors_master.json"):
    """
    Saves the master sensor data as JSON.
    Good Practice: JSON is native for web-like structures and handles 
    nested lists (coordinates) without complex serialization.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, indent=2)
    logging.info(f"Sensor master saved to {output_path}")

if __name__ == "__main__":
    # Example usage for generation
    # We use a recent file to ensure we have the most sensors
    sample_file = "data/raw/2025/12/22/traffic_121005.json"
    df_master = extract_sensor_geometries(sample_file)
    if not df_master.empty:
        save_sensor_master(df_master)
