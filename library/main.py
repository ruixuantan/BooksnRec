import os
import uuid
from datetime import date
from typing import Optional

import dotenv
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

dotenv.load_dotenv()
app = FastAPI()


class LoanCreate(BaseModel):
    reader_id: uuid.UUID
    book_id: int
    reserve_date: Optional[date]
    loan_date: Optional[date]
    return_date: Optional[date]


class Database:
    """
    Database context manager
    """

    def __init__(self) -> None:
        self.driver = psycopg2

    def connect_to_database(self):
        return self.driver.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()


@app.get("/readers")
async def get_reader_ids():
    with Database() as db:
        db.cursor.execute("SELECT id FROM Readers")
        readers = db.cursor.fetchall()
        readers = [id for row in readers for id in row]
        return {"readers": readers}


@app.post("/loans")
async def create_loan(loan: LoanCreate):
    with Database() as db:
        db.cursor.execute(
            f"""
            INSERT INTO Loans (id, reader_id, book_id, reserve_date, loan_date, return_date)
            VALUES (default, {loan.reader_id}, {loan.book_id}, {loan.reserve_date}, {loan.loan_date}, {loan.return_date})
        """
        )
        db.connection.commit()
        return {"status": "ok"}


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
