import csv
from typing import Dict, Iterator, List

from dateutil import parser


def _read_file(file_path: str) -> Iterator[Dict[str, str]]:
    with open(file_path, "r") as f:
        book_file = csv.DictReader(f, delimiter=",")
        for book in book_file:
            yield book


def _book_to_csv_row(book: Dict[str, str]) -> str:
    id = int(book["bookID"])
    title = book["title"]
    average_rating = int(book["average_rating"].replace(".", ""))
    isbn10 = book["isbn"]
    isbn13 = book["isbn13"]
    language_code = book["language_code"]
    num_pages = int(book["  num_pages"])
    ratings_count = int(book["ratings_count"])
    text_reviews = int(book["text_reviews_count"])
    try:
        publish_date = parser.parse(book["publication_date"]).strftime("%Y-%m-%d")
    except ValueError:
        publish_date = ""
    publisher = book["publisher"]
    row = (
        f"{id},{title},{average_rating},{isbn10},{isbn13},{language_code},"
        f"{num_pages},{ratings_count},{text_reviews},{publish_date},{publisher}\n"
    )
    return row


def write_books_csv_file(file_path: str, outfile_path: str):
    books = _read_file(file_path)
    header = (
        "B_ID,B_TITLE,B_AVERAGE_RATING,B_ISBN10,B_ISBN13,B_LANGUAGE_CODE,"
        "B_NUM_PAGES,B_RATINGS_COUNT,B_TEXT_REVIEWS,B_PUBLISH_DATE,B_PUBLISHER\n"
    )
    with open(outfile_path, "w") as f:
        f.write(header)
        for book in books:
            row = _book_to_csv_row(book)
            f.write(row)


def _get_written_rows(
    books: Iterator[Dict[str, str]],
    authors_id: Dict[str, int],
    delimiters: List[str] = ["/", ";"],
) -> Iterator[List[str]]:
    id = 0
    for book in books:
        authors = book["authors"]
        for delimiter in delimiters:
            if delimiter in authors:
                authors = authors.split(delimiter)
                break
        else:
            authors = [authors]

        for i in range(len(authors)):
            a = authors[i]
            authors[i] = " ".join([sub_name.lower() for sub_name in a.split()])

        for author in authors:
            if author not in authors_id:
                authors_id[author] = id
                id += 1

        book_id = int(book["bookID"])
        written = []
        for author in authors:
            written.append(f"{book_id},{authors_id[author]}\n")
        yield written


def write_authors_written_csv_file(
    file_path: str,
    authors_file: str,
    written_file: str,
    delimiters: List[str] = ["/", ";"],
):
    books = _read_file(file_path)
    authors_id = dict()
    written_rows = _get_written_rows(books, authors_id, delimiters)
    with open(written_file, "w") as f:
        f.write("W_AUTHOR_ID,W_BOOK_ID\n")
        for rows in written_rows:
            for row in rows:
                f.write(row)

    with open(authors_file, "w") as f:
        f.write("A_ID,A_NAME\n")
        for name in authors_id.keys():
            f.write(f"{authors_id[name]},{name}\n")
