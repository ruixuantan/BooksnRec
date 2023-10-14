import os

from minio import Minio


class MinioClient:
    endpoint: str
    access_key: str
    secret_key: str
    client: Minio

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=secure,
        )

    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        self.client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        self.client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )


MINIO = MinioClient(
    f"{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_PORT')}",
    os.getenv("MINIO_ROOT_USER"),
    os.getenv("MINIO_ROOT_PASSWORD"),
    secure=True if os.getenv("MINIO_SECURE") == "1" else False,
)
