from datetime import datetime

from clients.clickhouse_client import CLICKHOUSE
from clients.minio_client import MINIO

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from scripts.python.insert_raw_books_data import (
    write_authors_written_csv_file,
    write_books_csv_file,
)

BOOKS_FILE_PATH = "/tmp/books.csv"
PARSED_BOOKS_FILE_PATH = "/tmp/parsed_books.csv"
AUTHORS_FILE_PATH = "/tmp/authors.csv"
WRITTEN_FILE_PATH = "/tmp/written.csv"


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
    download_raw_data = PythonOperator(
        task_id="download_raw_books_data",
        python_callable=MINIO.download_file,
        op_kwargs={
            "bucket_name": "raw",
            "object_name": "books.csv",
            "file_path": BOOKS_FILE_PATH,
        },
    )

    write_books_csv = PythonOperator(
        task_id="write_books_csv_file",
        python_callable=write_books_csv_file,
        op_kwargs={
            "file_path": BOOKS_FILE_PATH,
            "outfile_path": PARSED_BOOKS_FILE_PATH,
        },
    )

    write_authors_csv = PythonOperator(
        task_id="write_authors_written_csv_file",
        python_callable=write_authors_written_csv_file,
        op_kwargs={
            "file_path": BOOKS_FILE_PATH,
            "authors_file": AUTHORS_FILE_PATH,
            "written_file": WRITTEN_FILE_PATH,
        },
    )

    upload_books_csv = PythonOperator(
        task_id="upload_parsed_books_data",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "dim_books",
            "file_path": PARSED_BOOKS_FILE_PATH,
        },
    )

    upload_authors_csv = PythonOperator(
        task_id="upload_authors_data",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "dim_authors",
            "file_path": AUTHORS_FILE_PATH,
        },
    )

    upload_written_csv = PythonOperator(
        task_id="upload_written_data",
        python_callable=CLICKHOUSE.upload_csv_file,
        op_kwargs={
            "table": "dim_written",
            "file_path": WRITTEN_FILE_PATH,
        },
    )

    remove_files = BashOperator(
        task_id="remove_files",
        bash_command=f"rm {BOOKS_FILE_PATH} {PARSED_BOOKS_FILE_PATH} {AUTHORS_FILE_PATH} {WRITTEN_FILE_PATH}",
        trigger_rule="all_success",
    )

    download_raw_data >> write_books_csv >> upload_books_csv >> remove_files
    (
        download_raw_data
        >> write_authors_csv
        >> upload_authors_csv
        >> upload_written_csv
        >> remove_files
    )
