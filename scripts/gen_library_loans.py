import asyncio
import json
import random
from dataclasses import dataclass

import aiohttp
import requests
from faker import Faker

URL = "http://localhost:8000/"
RESERVE_DATE_P = 0.1
LOAN_DATE_P = 0.8
NUM_LOANS = 100


@dataclass
class Loan:
    reader_id: int
    book_id: int
    reserve_date: str
    loan_date: str
    return_date: str


class LoanGenerator:
    def __init__(self, reader_ids, book_ids):
        self.reader_ids = reader_ids
        self.book_ids = book_ids
        random.shuffle(self.book_ids)
        self.f = Faker()

    def gen_loan(self) -> Loan:
        reader_id = random.choice(self.reader_ids)
        book_id = self.book_ids.pop()
        reserve_date = (
            self.f.date_between(start_date="-1m", end_date="today")
            if random.uniform(0, 1) < RESERVE_DATE_P
            else None
        )
        if reserve_date:
            loan_date = (
                self.f.date_between(start_date=reserve_date, end_date="today")
                if random.uniform(0, 1) < LOAN_DATE_P
                else None
            )
        else:
            loan_date = self.f.date_between(start_date="-2w", end_date="today")
        return_date = (
            self.f.date_between(start_date=loan_date, end_date="today")
            if loan_date
            else None
        )
        return Loan(
            reader_id=reader_id,
            book_id=book_id,
            reserve_date=str(reserve_date) if reserve_date else None,
            loan_date=str(loan_date) if loan_date else None,
            return_date=str(return_date) if return_date else None,
        )


def get_loan_generator() -> LoanGenerator:
    req = requests.get(URL + "readers")
    readers = req.json()["readers"]
    req = requests.get(URL + "books")
    books = req.json()["books"]
    return LoanGenerator(readers, books)


async def async_loop(x):
    for i in range(x):
        yield i


async def make_loans(loan_generator: LoanGenerator):
    async with aiohttp.ClientSession() as session:
        post_tasks = []
        async for _ in async_loop(NUM_LOANS):
            loan = loan_generator.gen_loan()
            post_tasks.append(do_post(session, loan))
        await asyncio.gather(*post_tasks)


async def do_post(session: aiohttp.ClientSession, loan: Loan):
    async with session.post(
        URL + "loans",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "reader_id": loan.reader_id,
                "book_id": loan.book_id,
                "reserve_date": loan.reserve_date,
                "loan_date": loan.loan_date,
                "return_date": loan.return_date,
            }
        ),
    ) as response:
        await response.text()


if __name__ == "__main__":
    loan_generator = get_loan_generator()
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(make_loans(loan_generator))
    finally:
        loop.close()
