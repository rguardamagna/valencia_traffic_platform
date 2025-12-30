import pandas as pd
import numpy as np
import logging

def extract_temporal_features(df):
    """
    Translates a timestamp into cyclical sine/cosine features.
    Ensures the model understands that 23:59 and 00:01 are close.
    """
    df = df.copy()
    # Ensure ingested_at is datetime
    df['dt'] = pd.to_datetime(df['ingested_at'])
    df['dt_rounded'] = df['dt'].dt.round('5min')
    
    # Extract raw hour and day
    hour = df['dt_rounded'].dt.hour
    day_of_week = df['dt_rounded'].dt.dayofweek
    
    # Apply Cyclical Encoding
    df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * hour / 24)
    df['day_sin'] = np.sin(2 * np.pi * day_of_week / 7)
    df['day_cos'] = np.cos(2 * np.pi * day_of_week / 7)
    
    return df

def prepare_inference_features(recent_snapshots_df):
    """
    The 'Translator' for production.
    Takes a window of recent data (at least 3-4 snapshots) 
    and prepares the feature vector for the LATEST snapshot.
    """
    if recent_snapshots_df.empty:
        return pd.DataFrame()

    # 1. Basic Cleaning
    df = recent_snapshots_df[recent_snapshots_df['estado'] != 9].copy()
    
    # 2. Add Temporal Features (Sin/Cos)
    df = extract_temporal_features(df)
    
    # 3. Sort for Lag Calculation
    # idtramo and dt_rounded are essential for the sequence
    df = df.sort_values(['idtramo', 'dt_rounded'])
    
    # 4. Calculate Lags (Memory)
    # The model expects estado_lag_1, 2, 3
    for lag in [1, 2, 3]:
        df[f'estado_lag_{lag}'] = df.groupby('idtramo')['estado'].shift(lag)
    
    # 5. Filter for only the LATEST time point available
    # We want to predict for the 'now' (latest ingested_at)
    latest_ts = df['dt_rounded'].max()
    latest_data = df[df['dt_rounded'] == latest_ts].copy()
    
    # 6. Final Feature Selection
    # These must match exactly the features the model was trained on
    ml_features = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 
        'estado_lag_1', 'estado_lag_2', 'estado_lag_3'
    ]
    
    # Drop rows that don't have enough history for lags
    # This might happen for new sensors or if history is too short
    return latest_data.dropna(subset=ml_features), ml_features

if __name__ == "__main__":
    # Test script with dummy data
    print("Testing inference_utils...")
    # ... test logic could go here
