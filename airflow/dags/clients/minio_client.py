from __future__ import annotations

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

    @classmethod
    def from_env(cls) -> MinioClient:
        return cls(
            f"{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_PORT')}",
            os.getenv("MINIO_ROOT_USER"),
            os.getenv("MINIO_ROOT_PASSWORD"),
            secure=True if os.getenv("MINIO_SECURE") == "1" else False,
        )

    @classmethod
    def download_file(cls, bucket_name: str, object_name: str, file_path: str):
        cls.from_env().client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )

    @classmethod
    def upload_file(cls, bucket_name: str, object_name: str, file_path: str):
        cls.from_env().client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )
