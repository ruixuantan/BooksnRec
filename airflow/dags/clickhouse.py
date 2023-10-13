import os

import clickhouse_connect
from clickhouse_connect.driver.client import Client


class Clickhouse:
    user: str
    password: str
    db: str
    client: Client

    def __init__(self, user: str, password: str, db: str, host: str, port: int):
        self.user = user
        self.password = password
        self.db = db
        self.client = clickhouse_connect.get_client(
            host=host,
            username=user,
            password=password,
            port=port,
        )

    def run(self, sql_stmt: str):
        self.client.command(sql_stmt)


CLICKHOUSE = Clickhouse(
    user=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
    db=os.getenv("CLICKHOUSE_DB"),
    host=os.getenv("CLICKHOUSE_HOST"),
    port=int(os.getenv("CLICKHOUSE_PORT")),
)
