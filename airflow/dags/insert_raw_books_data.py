from datetime import datetime

from insert_raw_books_data_h import (
    download_raw_books_data,
    insert_authors_to_clickhouse,
    insert_books_to_clickhouse,
)
from minio_client import MINIO

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from clickhouse import CLICKHOUSE

BOOKS_FILE_PATH = "/tmp/books.csv"


with DAG(
    "insert_raw_books_data",
    default_args={
        "depends_on_past": False,
        "email": [],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
    },
    description="Upload goodreads csv data into clickhouse",
    schedule=None,
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
) as dag:
    t1 = PythonOperator(
        task_id="download_raw_books_data",
        python_callable=download_raw_books_data,
        op_kwargs={
            "minio_client": MINIO,
            "bucket_name": "raw",
            "object_name": "books.csv",
            "file_path": BOOKS_FILE_PATH,
        },
    )

    t2 = PythonOperator(
        task_id="insert_books_data_to_clickhouse",
        python_callable=insert_books_to_clickhouse,
        op_kwargs={
            "file_path": BOOKS_FILE_PATH,
            "clickhouse": CLICKHOUSE,
        },
    )

    t3 = PythonOperator(
        task_id="insert_authors_data_to_clickhouse",
        python_callable=insert_authors_to_clickhouse,
        op_kwargs={
            "file_path": BOOKS_FILE_PATH,
            "clickhouse": CLICKHOUSE,
        },
    )

    t4 = BashOperator(
        task_id="remove_raw_books_data",
        bash_command=f"rm {BOOKS_FILE_PATH}",
    )

    t1 >> [t2, t3] >> t4
