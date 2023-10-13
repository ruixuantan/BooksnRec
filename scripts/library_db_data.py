import csv
import os
import random
import uuid

from faker import Faker

NUM_BOOKS = 8000
NUM_READERS = 1000
GENDER_SKEW = 0.5
DOB_PRESENCE = 0.9
MAX_BOOK_COPIES = 5
BOOK_COPY_P = 0.95

BOOKS_DATA = os.path.join("dataset", "books.csv")
SEED_BOOKS_FILE = os.path.join("library-db", "seed_data", "books.csv")
SEED_READERS_FILE = os.path.join("library-db", "seed_data", "readers.csv")


def get_num_geom_failures(p: float, maximum: int) -> int:
    n = 1
    counter = 0
    while random.uniform(0, 1) > p and counter <= maximum:
        n += 1
        counter += 1
    return n


def n_digit_rand(n) -> int:
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)


def get_num_books() -> int:
    with open(BOOKS_DATA, "r") as f:
        return len(f.readlines()) - 1


def gen_books(output_file: str = SEED_BOOKS_FILE):
    p = NUM_BOOKS / get_num_books()
    books = []
    with open(BOOKS_DATA, "r") as f:
        book_file = csv.DictReader(f, delimiter=",")
        for book in book_file:
            if random.uniform(0, 1) < p:
                copies = get_num_geom_failures(BOOK_COPY_P, MAX_BOOK_COPIES)
                for _ in range(copies):
                    books.append([book["title"], book["isbn"], book["isbn13"]])

    random.shuffle(books)
    id = 0
    with open(output_file, "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["id", "title", "isbn", "isbn13"])
        for book in books:
            row = [id] + book
            writer.writerow(row)
            id += 1


def gen_readers(output_file: str = SEED_READERS_FILE):
    f = Faker()
    with open(output_file, "w") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(
            [
                "id",
                "card_no",
                "name",
                "mobile_no",
                "email",
                "gender",
                "dob",
                "registered_on",
            ]
        )

        for _ in range(NUM_READERS):
            id = uuid.uuid4()
            card_no = n_digit_rand(10)
            mobile_no = n_digit_rand(8)
            gender = 1 if random.uniform(0, 1) < GENDER_SKEW else 2
            first_name = f.first_name_male() if gender == 1 else f.first_name_female()
            last_name = f.last_name()
            name = f"{first_name} {last_name}"
            email = f"{first_name.lower()}.{last_name.lower()}@{f.domain_name()}"
            dob = (
                f.date_of_birth(minimum_age=1, maximum_age=90)
                if random.uniform(0, 1) < DOB_PRESENCE
                else None
            )
            registered_on = (
                f.date_between() if dob is None else f.date_between(dob, "today")
            )

            writer.writerow(
                [id, card_no, name, mobile_no, email, gender, dob, registered_on]
            )


if __name__ == "__main__":
    gen_books()
    gen_readers()
