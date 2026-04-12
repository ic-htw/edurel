from edurel.core.duckdb_man import DuckDbMan


def test_export_data_as_insert_statements_exports_rows_with_sql_literals() -> None:
    db = DuckDbMan.fromMem("test_db")
    try:
        db.execute(
            """
            CREATE TABLE status_codes (
              ID INTEGER,
              Description VARCHAR,
              IsValid BOOLEAN,
              SortOrder INTEGER
            );
            """
        )
        db.execute(
            """
            INSERT INTO status_codes VALUES
              (1, 'Open', TRUE, 1),
              (2, 'Owner''s Review', FALSE, 2);
            """
        )

        assert db.export_data_as_insert_statements(["status_codes"]) == (
            "-- Table: status_codes\n"
            "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) "
            "VALUES (1, 'Open', TRUE, 1);\n"
            "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) "
            "VALUES (2, 'Owner''s Review', FALSE, 2);"
        )
    finally:
        db.close()


def test_export_data_as_insert_statements_preserves_requested_table_order() -> None:
    db = DuckDbMan.fromMem("test_db")
    try:
        db.execute(
            """
            CREATE TABLE users (
              id INTEGER,
              email VARCHAR,
              signup_date DATE
            );
            """
        )
        db.execute(
            """
            CREATE TABLE enrollments (
              id INTEGER,
              user_id INTEGER,
              notes VARCHAR
            );
            """
        )
        db.execute("INSERT INTO users VALUES (1, NULL, DATE '2026-04-12');")
        db.execute("INSERT INTO enrollments VALUES (10, 1, 'late join');")

        assert db.export_data_as_insert_statements(["enrollments", "users"]) == (
            "-- Table: enrollments\n"
            "INSERT INTO enrollments (id, user_id, notes) VALUES (10, 1, 'late join');\n"
            "\n"
            "-- Table: users\n"
            "INSERT INTO users (id, email, signup_date) VALUES (1, NULL, '2026-04-12');"
        )
    finally:
        db.close()
