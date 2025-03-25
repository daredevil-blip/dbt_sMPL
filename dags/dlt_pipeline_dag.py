from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

sys.path.append('/opt/airflow/dlt_ingestion')

def run_dlt_pipeline():
    os.environ["DESTINATION__POSTGRES__CREDENTIALS"] = "postgres://airflow:airflow@postgres:5432/airflow"
    from pipeline import pipeline_main
    pipeline_main()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 1),
    'retries': 1,
}

with DAG(
    dag_id='dlt_to_postgres_pipeline',
    default_args=default_args,
    description='DLT -> Postgres Airflow Pipeline',
    schedule_interval=None,
    catchup=False,
) as dag:

    run_pipeline_task = PythonOperator(
        task_id='run_dlt_pipeline_task',
        python_callable=run_dlt_pipeline
    )

    run_pipeline_task
