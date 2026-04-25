import pytest

from edurel.utils.sql import transpile_postgres_sql, validate_postgres_sql


def test_validate_postgres_sql_accepts_valid_sql() -> None:
    assert validate_postgres_sql("SELECT 1;") is None


def test_validate_postgres_sql_raises_value_error_with_location_details() -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_postgres_sql("SELECT FROM")

    message = str(exc_info.value)
    assert "SQL validation failed." in message
    assert "Location: line 1, column 11." in message
    assert "Problem: Expected table name" in message
    assert "Context: PostgreSQL parsing failed." in message
    assert "Snippet: SELECT FROM" in message
    assert "Potential fix:" in message


def test_transpile_postgres_sql_returns_target_dialect_sql() -> None:
    assert (
        transpile_postgres_sql("SELECT 'a' ILIKE 'A';", "sqlite")
        == "SELECT LOWER('a') LIKE LOWER('A')"
    )


def test_transpile_postgres_sql_raises_value_error_for_invalid_sql() -> None:
    with pytest.raises(ValueError) as exc_info:
        transpile_postgres_sql("SELECT FROM", "sqlite")

    message = str(exc_info.value)
    assert "SQL validation failed." in message
    assert "Location: line 1, column 11." in message
