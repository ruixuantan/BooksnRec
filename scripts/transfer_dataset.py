import os

from dotenv import load_dotenv
from minio.error import S3Error

from minio import Minio

load_dotenv()

MINIO_URL = f"localhost:{os.getenv('MINIO_PORT')}"
ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET = os.getenv("MINIO_RAW_BUCKET")
SECURE = True if os.getenv("MINIO_SECURE") == "1" else False


def upload():
    client = Minio(
        MINIO_URL,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False,
    )
    if not client.bucket_exists(BUCKET):
        raise Exception(f"Bucket {BUCKET} does not exist")

    client.fput_object(
        bucket_name=BUCKET,
        object_name="books.csv",
        file_path=os.path.join("dataset", "books.csv"),
    )


if __name__ == "__main__":
    try:
        upload()
    except S3Error as exc:
        print(f"error occurred: {exc}")
