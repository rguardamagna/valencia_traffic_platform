from airflow import DAG
from airflow.operators.bash import BashOperator
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
    'verify_deployment_v1',
    default_args=default_args,
    description='A simple DAG to verify CD pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['verification'],
) as dag:

    t1 = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hola Mundo! El despliegue funciona correctamente."',
    )
