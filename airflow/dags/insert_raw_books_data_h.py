import csv
from typing import Dict, Iterator, List, Tuple

from dateutil import parser
from minio_client import MinioClient

from clickhouse import Clickhouse


def _read_file(file_path: str) -> Iterator[Dict[str, str]]:
    with open(file_path, "r") as f:
        book_file = csv.DictReader(f, delimiter=",")
        for book in book_file:
            yield book


def _get_book_value_sql_stmt(data: Dict[str, str]) -> str:
    id = int(data["bookID"])
    title = data["title"].replace("'", "''")
    average_rating = int(data["average_rating"].replace(".", ""))
    isbn10 = data["isbn"]
    isbn13 = data["isbn13"]
    language_code = data["language_code"]
    num_pages = int(data["  num_pages"])
    ratings_count = int(data["ratings_count"])
    text_reviews = int(data["text_reviews_count"])
    try:
        publish_date = parser.parse(data["publication_date"]).strftime("%Y-%m-%d")
    except ValueError:
        publish_date = "NULL"
    publisher = data["publisher"].replace("'", "''")
    sql_stmt = (
        f"({id}, '{title}', {average_rating}, '{isbn10}', '{isbn13}', "
        f"'{language_code}', {num_pages}, {ratings_count}, "
        f"{text_reviews}, '{publish_date}', '{publisher}')"
    )
    return sql_stmt


def _get_books_insert_stmt(data: List[str]) -> str:
    sql_stmt = f"INSERT INTO dim_books VALUES {','.join(data)}"
    return sql_stmt


def download_raw_books_data(
    minio_client: MinioClient, bucket_name: str, object_name: str, file_path: str
):
    minio_client.download_file(
        bucket_name=bucket_name,
        object_name=object_name,
        file_path=file_path,
    )


def insert_books_to_clickhouse(
    file_path: str, clickhouse: Clickhouse, batch_size: int = 10000
):
    books = _read_file(file_path)
    stmts = []
    try:
        while book := books.__next__():
            sql_stmt = _get_book_value_sql_stmt(book)
            stmts.append(sql_stmt)
            if len(stmts) == batch_size:
                stmt = _get_books_insert_stmt(stmts)
                stmts = []
                clickhouse.run(stmt)
    except StopIteration:
        stmt = _get_books_insert_stmt(stmts)
        clickhouse.run(stmt)


def _get_author_value_sql_stmt(authors: Dict[str, str]) -> str:
    stmts = []
    for name in authors.keys():
        stmts.append(f"({authors[name]}, '{name}')")
    return f"INSERT INTO dim_authors VALUES {','.join(stmts)}"


def _get_written_value_sql_stmt(written: List[Tuple[str]]) -> str:
    stmts = []
    for book_id, author_id in written:
        stmts.append(f"({book_id}, {author_id})")
    return f"INSERT INTO dim_written VALUES {','.join(stmts)}"


def insert_authors_to_clickhouse(
    file_path: str, clickhouse: Clickhouse, delimiters: List[str] = ["/", ";"]
):
    books = _read_file(file_path)
    authors_id = dict()
    written = []
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
            authors[i] = " ".join(
                [sub_name.replace("'", "''").lower() for sub_name in a.split()]
            )

        for author in authors:
            if author not in authors_id:
                authors_id[author] = id
                id += 1

        book_id = int(book["bookID"])
        for author in authors:
            written.append((book_id, authors_id[author]))

    author_stmt = _get_author_value_sql_stmt(authors_id)
    clickhouse.run(author_stmt)
    written_stmt = _get_written_value_sql_stmt(written)
    clickhouse.run(written_stmt)
