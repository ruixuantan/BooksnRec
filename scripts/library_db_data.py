import csv
import random
import uuid

from faker import Faker

NUM_BOOKS = 1000
NUM_READERS = 200
GENDER_SKEW = 0.5
DOB_PRESENCE = 0.9

BOOKS_DATA = "dataset/books.csv"


def n_digit_rand(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)


def get_num_books() -> int:
    with open(BOOKS_DATA, "r") as f:
        return len(f.readlines()) - 1


def gen_books(output_file: str = "library-db/books.csv"):
    p = NUM_BOOKS / get_num_books()
    books = []
    id = 0
    with open(BOOKS_DATA, "r") as f:
        book_file = csv.DictReader(f, delimiter=",")
        for book in book_file:
            if random.uniform(0, 1) < p:
                books.append((id, book["title"], book["isbn"], book["isbn13"]))
                id += 1

    with open(output_file, "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["id", "title", "isbn", "isbn13"])
        for book in books:
            writer.writerow(book)


def gen_readers(output_file: str = "library-db/readers.csv"):
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
