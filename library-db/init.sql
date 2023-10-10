DROP TABLE IF EXISTS
    Readers,
    Books,
    Loans,
CASCADE;

CREATE TABLE Readers(
    id UUID PRIMARY KEY,
    card_no CHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    mobile_no CHAR(8) NOT NULL,
    email VARCHAR(255) NOT NULL,
    gender CHAR(1) NOT NULL,
    dob DATE,
    registered_on DATE NOT NULL
);

CREATE TABLE Books(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    isbn10 CHAR(10) NOT NULL,
    isbn13 CHAR(13) NOT NULL
);

CREATE TABLE Loans(
    id BIGSERIAL PRIMARY KEY,
    reader_id UUID NOT NULL,
    book_id SERIAL NOT NULL,
    reserve_date DATE,
    loan_date DATE,
    return_date DATE,
    FOREIGN KEY (reader_id) REFERENCES Readers(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);

COPY Readers FROM '/var/lib/postgresql/seed_data/readers.csv' DELIMITER ',' CSV HEADER;
COPY Books FROM '/var/lib/postgresql/seed_data/books.csv' DELIMITER ',' CSV HEADER;
