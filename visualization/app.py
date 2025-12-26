import streamlit as st
import pandas as pd
import json
from pathlib import Path
import folium
from streamlit_folium import folium_static
import sys
import os
import joblib
from xgboost import XGBClassifier
import numpy as np

# Add src to path for data loading utilities
sys.path.append(os.path.abspath("."))
from src.refining.data_loader import load_historical_data

# Page Configuration
st.set_page_config(
    page_title="Valencia Traffic Spotlight",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Singleton Patterns (Good Practice: Performance) ---

@st.cache_resource
def load_sensors():
    """Load static sensor geometries."""
    with open("data/sensors_master.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def get_latest_traffic():
    """Find and load the most recent JSON snapshot."""
    base_raw = Path("data/raw")
    all_files = sorted(list(base_raw.rglob("*.json")), key=os.path.getmtime, reverse=True)
    if not all_files:
        return pd.DataFrame()
    
    # Use our existing data_loader but for a single file (or a few recent ones)
    df = load_historical_data(str(all_files[0].parent))
    # Filter for only the latest snapshot in that folder
    latest_ts = df['ingested_at'].max()
    return df[df['ingested_at'] == latest_ts]

@st.cache_resource
def load_oracle_model():
    """Placeholder to load the trained model. 
    In a real scenario, we would use a saved .joblib or .json from XGBoost.
    """
    # For now, we point to where the model should be.
    # If not found, we will return None.
    model_path = "models/champion_xgboost.joblib"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

# --- Helper Functions ---

def get_status_color(status):
    """Map Valencia status codes to colors.
    0: Fluido (Green)
    1: Denso (Orange)
    2: Muy denso (Red)
    3: Congestión (Dark Red)
    5: Cortado (Black)
    9: Sin datos (Gray)
    """
    colors = {
        0: "#2ecc71", # Green
        1: "#f39c12", # Orange
        2: "#e74c3c", # Red
        3: "#8b0000", # Dark Red
        5: "#000000", # Black
        9: "#95a5a6", # Gray
    }
    return colors.get(int(status) if not pd.isna(status) else 9, "#95a5a6")

# --- UI Components ---

st.sidebar.title("🚦 The Spotlight")
st.sidebar.markdown("### Valencia Traffic Platform")

# App Mode
app_mode = st.sidebar.radio("Ver modo:", ["Estado Actual", "The Oracle (Predicción)"])

st.sidebar.divider()
st.sidebar.info("""
**Leyenda de Tráfico:**
- 🟢 Fluido
- 🟠 Denso
- 🔴 Muy Denso
- 🟤 Congestión
- ⚫ Cortado
""")

# --- Main Logic ---

st.title("Valencia Real-Time Traffic Monitor")

# Data Loading
sensors_df = load_sensors()
traffic_df = get_latest_traffic()

if traffic_df.empty:
    st.error("No se ha encontrado información de tráfico reciente.")
else:
    # Merge current data with geometries
    # Good Practice: Select only needed columns to avoid name collisions (e.g., 'denominacion')
    traffic_subset = traffic_df[['idtramo', 'estado', 'ingested_at']]
    merged_df = pd.merge(sensors_df, traffic_subset, on='idtramo', how='inner')
    
    # Date and Time Info
    last_update = merged_df['ingested_at'].iloc[0]
    st.caption(f"Última actualización: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Map Creation
    # Center on Valencia City Hall
    m = folium.Map(location=[39.4699, -0.3763], zoom_start=14, tiles="cartodbpositron")

    for _, row in merged_df.iterrows():
        status = row['estado']
        color = get_status_color(status)
        
        # Oracle Mode: Apply basic prediction logic 
        # (This is a simplified implementation for the E2E demo)
        if app_mode == "The Oracle (Predicción)":
            # In a real scenario, we would run: model.predict(X_current)
            # Here we just keep current to show the capability
            st.sidebar.warning("Oracle Mode: Mostrando proyección a +15 min (Simulada)")
        
        folium.PolyLine(
            locations=row['coordinates'],
            color=color,
            weight=5,
            opacity=0.8,
            popup=f"Tramo: {row['denominacion']} (ID: {row['idtramo']})<br>Estado: {status}"
        ).add_to(m)

    # Display Map
    folium_static(m, width=1000, height=600)

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sensores Activos", len(merged_df))
    with col2:
        congestion_pct = (merged_df['estado'].isin([1,2,3]).sum() / len(merged_df)) * 100
        st.metric("Zonas en Congestión", f"{congestion_pct:.1f}%")
    with col3:
        st.metric("Estado General", "Estable" if congestion_pct < 10 else "Crítico")
