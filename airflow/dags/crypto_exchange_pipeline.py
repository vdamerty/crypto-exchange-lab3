import shlex
import sys
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


# Знаходимо корінь проєкту відносно цього файлу.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Дозволяємо імпортувати наш генератор із папки scripts.
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from data_generator import load_data_to_dwh


DBT_EXECUTABLE = PROJECT_ROOT / ".venv-dbt" / "bin" / "dbt"
DBT_PROJECT_DIR = PROJECT_ROOT / "crypto_dbt"


def dbt_command(command):
    return shlex.join(
        [
            str(DBT_EXECUTABLE),
            command,
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(DBT_PROJECT_DIR),
        ]
    )


default_args = {
    "owner": "data_engineer",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2026, 1, 1, tz="UTC"),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="crypto_exchange_elt_pipeline",
    default_args=default_args,
    description="ELT-конвеєр криптобіржі — варіант 9",
    schedule_interval="@daily",
    catchup=False,
    max_active_runs=1,
    tags=["lab3", "variant9", "crypto"],
) as dag:

    extract_load_task = PythonOperator(
        task_id="extract_and_load_raw_data",
        python_callable=load_data_to_dwh,
    )

    dbt_run_task = BashOperator(
        task_id="dbt_run_transformations",
        bash_command=dbt_command("run"),
    )

    dbt_test_task = BashOperator(
        task_id="dbt_test_quality_gate",
        bash_command=dbt_command("test"),
    )

    extract_load_task >> dbt_run_task >> dbt_test_task