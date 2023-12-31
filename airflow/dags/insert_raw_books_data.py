from datetime import datetime

from clients.clickhouse_client import Clickhouse
from clients.minio_client import MinioClient as Minio

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
        python_callable=Minio.download_file,
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

    upload_books_csv_to_minio = PythonOperator(
        task_id="upload_parsed_books_data_to_minio",
        python_callable=Minio.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "books/{{ ds }}/books.csv",
            "file_path": PARSED_BOOKS_FILE_PATH,
        },
    )

    upload_books_csv_to_clickhouse = PythonOperator(
        task_id="upload_parsed_books_data_to_clickhouse",
        python_callable=Clickhouse.upload_csv_file,
        op_kwargs={
            "table": "dim_books",
            "file_path": PARSED_BOOKS_FILE_PATH,
        },
    )

    upload_authors_csv_to_minio = PythonOperator(
        task_id="upload_authors_data_to_minio",
        python_callable=Minio.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "authors/{{ ds }}/authors.csv",
            "file_path": AUTHORS_FILE_PATH,
        },
    )

    upload_authors_csv_to_clickhouse = PythonOperator(
        task_id="upload_authors_data_to_clickhouse",
        python_callable=Clickhouse.upload_csv_file,
        op_kwargs={
            "table": "dim_authors",
            "file_path": AUTHORS_FILE_PATH,
        },
    )

    upload_written_csv_to_minio = PythonOperator(
        task_id="upload_written_data_to_minio",
        python_callable=Minio.upload_file,
        op_kwargs={
            "bucket_name": "stage",
            "object_name": "written/{{ ds }}/written.csv",
            "file_path": WRITTEN_FILE_PATH,
        },
    )

    upload_written_csv_to_clickhouse = PythonOperator(
        task_id="upload_written_data_to_clickhouse",
        python_callable=Clickhouse.upload_csv_file,
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

    (
        download_raw_data
        >> write_books_csv
        >> upload_books_csv_to_minio
        >> upload_books_csv_to_clickhouse
        >> remove_files
    )
    download_raw_data >> write_authors_csv
    (
        write_authors_csv
        >> upload_authors_csv_to_minio
        >> upload_authors_csv_to_clickhouse
        >> remove_files
    )
    (
        write_authors_csv
        >> upload_written_csv_to_minio
        >> upload_written_csv_to_clickhouse
        >> remove_files
    )
