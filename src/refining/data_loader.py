import json
import pandas as pd
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_historical_data(base_path: str = "../data/raw"):
    """
    Reads all JSON files in the specified base path and returns a consolidated DataFrame.
    """
    base_dir = Path(base_path)
    all_files = sorted(list(base_dir.rglob("*.json")))
    
    if not all_files:
        logging.warning(f"No JSON files found in {base_path}")
        return pd.DataFrame()

    logging.info(f"Loading {len(all_files)} files from {base_path}...")
    
    all_dfs = []
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'results' in data and data['results']:
                df_temp = pd.json_normalize(data['results'])
                
                # Add ingestion timestamp if available
                ingestion_ts = data.get('ingestion_metadata', {}).get('ingestion_timestamp')
                if ingestion_ts:
                    df_temp['ingested_at'] = pd.to_datetime(ingestion_ts)
                
                all_dfs.append(df_temp)
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    if not all_dfs:
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)
    
    # Basic sorting and unique handling
    if 'ingested_at' in df_final.columns:
        df_final = df_final.sort_values('ingested_at')
        
    logging.info(f"Total records loaded: {len(df_final)}")
    logging.info(f"Columns found: {list(df_final.columns)}")
    return df_final

if __name__ == "__main__":
    # Test loading
    df = load_historical_data("data/raw")
    if not df.empty:
        print(df.head())
        print(df.info())
