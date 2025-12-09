from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

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
        network_mode="bridge",
        # We mount the VPS path to the container path to persist data
        # IMPORTANT: Ensure '/opt/valencia_traffic_platform/data' exists on your VPS
        mounts=[
             "/opt/valencia_traffic_platform/data:/app/data"
        ]
    )

    ingest_task
