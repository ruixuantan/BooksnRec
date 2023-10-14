from datetime import datetime, timedelta

from clients.clickhouse_client import CLICKHOUSE
from clients.minio_client import MINIO

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from scripts.python.insert_daily_reader_loans_data import unload_loans_readers

READERS_FILE_PATH = "/tmp/readers.csv"
LOANS_FILE_PATH = "/tmp/loans.csv"
READER_METRICS_FILE_PATH = "/tmp/reader_metrics.csv"

DATE_FORMAT = "%Y-%m-%d"


with DAG(
    "insert_daily_reader_loans_data",
    default_args={
        "depends_on_past": False,
        "email": [],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
    },
    description="Upload reader, loans, reader metrics data on a daily basis into clickhouse",
    schedule_interval="@daily",
    start_date=datetime.now(),
) as dag:
    download_db_data = PythonOperator(
        task_id="download_db_data",
        python_callable=unload_loans_readers,
        op_kwargs={
            "start_date": (datetime.now() - timedelta(1)).strftime(DATE_FORMAT),
            "end_date": datetime.now().strftime(DATE_FORMAT),
            "readers_file": READERS_FILE_PATH,
            "loans_file": LOANS_FILE_PATH,
            "reader_metrics_file": READER_METRICS_FILE_PATH,
        },
    )

    upload_readers_data_to_minio = PythonOperator(
        task_id="upload_readers_data_to_minio",
        python_callable=MINIO.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "stage/readers/{{ ds }}/readers.csv",
            "file_path": READERS_FILE_PATH,
        },
    )

    upload_loans_data_to_minio = PythonOperator(
        task_id="upload_loans_data_to_minio",
        python_callable=MINIO.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "stage/loans/{{ ds }}/loans.csv",
            "file_path": LOANS_FILE_PATH,
        },
    )

    upload_reader_metrics_data_to_minio = PythonOperator(
        task_id="upload_reader_metrics_data_to_minio",
        python_callable=MINIO.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "stage/reader_metrics/{{ ds }}/reader_metrics.csv",
            "file_path": READER_METRICS_FILE_PATH,
        },
    )

    upload_readers_data_to_clickhouse = PythonOperator(
        task_id="upload_readers_data_to_clickhouse",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "dim_readers",
            "file_path": READERS_FILE_PATH,
        },
    )

    upload_loans_data_to_clickhouse = PythonOperator(
        task_id="upload_loans_data_to_clickhouse",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "dim_loans",
            "file_path": LOANS_FILE_PATH,
        },
    )

    upload_reader_metrics_data_to_clickhouse = PythonOperator(
        task_id="upload_reader_metrics_data_to_clickhouse",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "fact_reader_metrics",
            "file_path": READER_METRICS_FILE_PATH,
        },
    )

    remove_files = BashOperator(
        task_id="remove_files",
        bash_command=f"rm {READERS_FILE_PATH} {LOANS_FILE_PATH} {READER_METRICS_FILE_PATH}",
    )

    (
        download_db_data
        >> upload_readers_data_to_minio
        >> upload_readers_data_to_clickhouse
        >> remove_files
    )
    (
        download_db_data
        >> upload_loans_data_to_minio
        >> upload_loans_data_to_clickhouse
        >> remove_files
    )
    (
        download_db_data
        >> upload_reader_metrics_data_to_minio
        >> upload_reader_metrics_data_to_clickhouse
        >> remove_files
    )
