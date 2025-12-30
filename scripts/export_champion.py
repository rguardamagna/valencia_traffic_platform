import os
import sys
import pandas as pd
import numpy as np
import logging
import joblib
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier

# Add project root to path to import src
sys.path.append(os.path.abspath("."))
from src.refining.data_loader import load_historical_data

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def prepare_data(df):
    """
    Apply feature engineering validated in the notebook.
    """
    logging.info("Preparing data...")
    df = df.copy()
    df['dt'] = pd.to_datetime(df['ingested_at'])
    df['dt_rounded'] = df['dt'].dt.round('5min')
    
    # Temporal features
    df['hour'] = df['dt_rounded'].dt.hour
    df['day_of_week'] = df['dt_rounded'].dt.dayofweek
    
    # Cyclical encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    # Filter out state 9 (no data)
    df = df[df['estado'] != 9].copy()
    
    # Sorting for lags
    df = df.sort_values(['idtramo', 'dt_rounded'])
    
    features = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos']
    for lag in [1, 2, 3]:
        col_name = f'estado_lag_{lag}'
        df[col_name] = df.groupby('idtramo')['estado'].shift(lag)
        features.append(col_name)
    
    # Drop rows with NaNs in features or target
    df = df.dropna(subset=features + ['estado'])
    return df, features

def main():
    # 1. Load Data
    raw_path = "data/raw/2025"
    if not os.path.exists(raw_path):
        # Fallback if specific year folder doesn't exist
        raw_path = "data/raw"
        
    df_raw = load_historical_data(raw_path)
    if df_raw.empty:
        logging.error("No data found to train. Exiting.")
        return

    # 2. Prepare Data
    data, ml_features = prepare_data(df_raw)
    logging.info(f"Dataset prepared with shape: {data.shape}")

    # 3. Define Train/Test Split
    X = data[ml_features]
    y = data['estado']
    
    # Shuffle=False to maintain temporal sequence
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    logging.info(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

    # 4. Handle Class Imbalance
    classes = np.unique(y_train)
    weights = compute_class_weight(
        class_weight='balanced', 
        classes=classes, 
        y=y_train
    )
    class_weights_dict = dict(zip(classes, weights))
    sample_weights = np.array([class_weights_dict[val] for val in y_train])
    logging.info(f"Computed class weights: {class_weights_dict}")

    # 5. Train Champion Model (XGBoost)
    logging.info("Training XGBoost Champion model...")
    champion_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        objective='multi:softprob'
    )

    champion_model.fit(X_train, y_train, sample_weight=sample_weights)
    logging.info("Model training complete.")

    # 6. Export Model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "champion_xgboost.joblib")
    
    joblib.dump(champion_model, model_path)
    logging.info(f"Champion model exported to: {model_path}")

if __name__ == "__main__":
    main()
