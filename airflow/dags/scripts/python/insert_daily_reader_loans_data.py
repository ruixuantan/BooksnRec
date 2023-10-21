from typing import Tuple

from airflow.hooks.postgres_hook import PostgresHook


def _get_data(func):
    def inner(start_date: str, end_date: str, outfile: str):
        header, sql, outfile = func(start_date, end_date, outfile)

        pg_hook = PostgresHook(postgres_conn_id="library-db")
        with pg_hook.get_conn() as pg_conn:
            with pg_conn.cursor() as cursor:
                cursor.execute(sql)
                with open(outfile, "w") as f:
                    f.write(header)
                    for row in cursor.fetchall():
                        f.write(",".join([str(x) if x else r"\N" for x in row]) + "\n")

    return inner


@_get_data
def _get_reader_sql(
    start_date: str, end_date: str, outfile: str
) -> Tuple[str, str, str]:
    header = "R_ID,R_NAME,R_GENDER,R_DOB\n"
    sql = (
        "SELECT id, name, gender, dob FROM Readers "
        f"WHERE registered_on >= '{start_date}' AND registered_on < '{end_date}'"
    )
    return header, sql, outfile


@_get_data
def _get_loan_sql(start_date: str, end_date: str, outfile: str) -> Tuple[str, str, str]:
    header = "L_ID,L_RESERVE_DATE,L_LOAN_DATE,L_RETURN_DATE\n"
    sql = (
        "SELECT id, reserve_date, loan_date, return_date FROM Loans "
        f"WHERE updated_on >= '{start_date}' AND updated_on < '{end_date}'"
    )
    return header, sql, outfile


@_get_data
def _get_reader_metrics_sql(start_date: str, end_date: str, outfile: str):
    header = "RM_LOAN_ID,RM_READER_ID,RM_BOOK_ISBN10\n"
    sql = (
        "SELECT Loans.id, Loans.reader_id, Books.isbn10 "
        "FROM Loans JOIN Books ON Loans.book_id = Books.id "
        f"WHERE Loans.updated_on >= '{start_date}' AND Loans.updated_on < '{end_date}'"
    )
    return header, sql, outfile


def unload_loans_readers(
    start_date: str,
    end_date: str,
    readers_file: str,
    loans_file: str,
    reader_metrics_file: str,
):
    _get_reader_sql(start_date, end_date, readers_file)
    _get_loan_sql(start_date, end_date, loans_file)
    _get_reader_metrics_sql(start_date, end_date, reader_metrics_file)
