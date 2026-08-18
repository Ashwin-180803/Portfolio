from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECTS = "/opt/airflow/projects"

with DAG(
    dag_id="citibike_daily",
    description="Ingest Citi Bike trips, rebuild the warehouse, then gate on quality.",
    start_date=datetime(2024, 6, 1),
    schedule="@daily",
    catchup=False,
    tags=["citibike", "portfolio"],
) as dag:
    ingest_lakehouse = BashOperator(
        task_id="ingest_lakehouse",
        bash_command=f"cd {PROJECTS}/citibike-lakehouse && python -m pipeline run",
    )
    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            f"cp {PROJECTS}/citibike-lakehouse/data/silver/trips.csv "
            f"{PROJECTS}/citibike-dbt-warehouse/seeds/trips.csv && "
            f"cd {PROJECTS}/citibike-dbt-warehouse && python -m warehouse run"
        ),
    )
    run_quality = BashOperator(
        task_id="run_quality",
        bash_command=(
            f"cd {PROJECTS}/data-quality-framework && "
            f"python -m quality run --data-root {PROJECTS}/citibike-lakehouse/data"
        ),
    )
    publish_status = BashOperator(
        task_id="publish_status",
        bash_command='echo "citibike_daily succeeded for {{ ds }}"',
    )

    ingest_lakehouse >> run_dbt >> run_quality >> publish_status
