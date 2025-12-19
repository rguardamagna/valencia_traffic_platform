from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from datetime import datetime, timedelta

from airflow.models import Variable
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Get configuration from Airflow Variables or environment
# Intentamos detectar la ruta del proyecto desde el entorno, si no, usamos /opt/ como base (más estándar que /root)
default_project_path = os.environ.get('AIRFLOW_PROJ_DIR', '/opt/valencia_traffic_platform')
PROJECT_DATA_PATH = Variable.get("valencia_traffic_data_path", default_var=f"{default_project_path}/data")
API_URL = os.environ.get("VALENCIA_TRAFFIC_API_URL", "https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estat-transit-temps-real-estado-trafico-tiempo-real/records")

with DAG(
    'valencia_traffic_ingestion',
    default_args=default_args,
    description='Ingest Valencia traffic data every 10 minutes',
    schedule_interval='*/10 * * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['valencia', 'traffic', 'ingestion'],
) as dag:

    # This task runs the Docker container defined by our image
    ingest_task = DockerOperator(
        task_id='ingest_traffic_data',
        image='valencia-traffic-ingestion:latest',
        api_version='auto',
        auto_remove=True,
        command="python src/ingestion/ingest_traffic.py",
        docker_url="unix://var/run/docker.sock",
        environment={
            "VALENCIA_TRAFFIC_API_URL": API_URL
        },
        mounts=[
            Mount(source=PROJECT_DATA_PATH, target='/app/data', type='bind')
        ]
    )

    ingest_task
