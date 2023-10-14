CREATE TABLE IF NOT EXISTS dim_readers (
    R_ID UUID,
    R_NAME String,
    R_GENDER Nullable(FixedString(1)),
    R_DOB Nullable(Date)
) ENGINE = MergeTree() ORDER BY (R_ID);

CREATE TABLE IF NOT EXISTS dim_books (
    B_ID UInt32,
    B_TITLE Nullable(String),
    B_AVERAGE_RATING Nullable(UInt16),
    B_ISBN10 FixedString(10),
    B_ISBN13 FixedString(13),
    B_LANGUAGE_CODE Nullable(String),
    B_NUM_PAGES Nullable(UInt16),
    B_RATINGS_COUNT Nullable(UInt16),
    B_TEXT_REVIEWS Nullable(UInt16),
    B_PUBLISH_DATE Nullable(Date),
    B_PUBLISHER Nullable(String)
) ENGINE = MergeTree() ORDER BY (B_ISBN10);

CREATE TABLE IF NOT EXISTS dim_authors (
    A_ID UInt32,
    A_NAME String
) ENGINE = MergeTree() ORDER BY (A_ID);

CREATE TABLE IF NOT EXISTS dim_written (
    W_AUTHOR_ID UInt32,
    W_BOOK_ID UInt32
) ENGINE = MergeTree() ORDER BY (W_AUTHOR_ID, W_BOOK_ID);

CREATE TABLE IF NOT EXISTS dim_loans (
    L_ID UInt32,
    L_RESERVE_DATE Nullable(Date),
    L_LOAN_DATE Nullable(Date),
    L_RETURN_DATE Nullable(Date)
) ENGINE = MergeTree() ORDER BY (L_ID);

CREATE TABLE IF NOT EXISTS fact_reader_metrics (
    RM_LOAN_ID UInt32,
    RM_READER_ID UUID,
    RM_BOOK_ISBN10 FixedString(10),
) ENGINE = MergeTree() ORDER BY (RM_LOAN_ID);
