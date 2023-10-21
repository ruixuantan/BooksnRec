from __future__ import annotations

import os

import clickhouse_connect
from clickhouse_connect.driver.client import Client
from clickhouse_connect.driver.tools import insert_file


class Clickhouse:
    user: str
    password: str
    db: str
    host: str
    port: str
    client: Client

    def __init__(self, user: str, password: str, db: str, host: str, port: int):
        self.user = user
        self.password = password
        self.db = db
        self.host = host
        self.port = port

    def __enter__(self):
        self.client = clickhouse_connect.get_client(
            host=self.host,
            username=self.user,
            password=self.password,
            port=self.port,
        )

    def __exit__(self, exception_type, exc_val, traceback):
        self.client.close()

    @classmethod
    def from_env(cls) -> Clickhouse:
        return cls(
            user=os.getenv("CLICKHOUSE_USER"),
            password=os.getenv("CLICKHOUSE_PASSWORD"),
            db=os.getenv("CLICKHOUSE_DB"),
            host=os.getenv("CLICKHOUSE_HOST"),
            port=int(os.getenv("CLICKHOUSE_PORT")),
        )

    @classmethod
    def run(cls, sql_stmt: str):
        clickhouse = cls.from_env()
        with clickhouse:
            clickhouse.client.command(sql_stmt)

    @classmethod
    def upload_csv_file(cls, table: str, file_path: str):
        clickhouse = cls.from_env()
        with clickhouse:
            insert_file(clickhouse.client, table, file_path)
