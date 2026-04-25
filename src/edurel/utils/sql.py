import re

import sqlglot
from sqlglot.errors import ParseError, UnsupportedError


def sql_extract(text: str) -> str:
    """Extract SQL code from text (supports both plain text and markdown)."""
    sql_block_pattern = r"```sql\s*\n(.*?)\n```"
    matches = re.findall(sql_block_pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    generic_block_pattern = r"```\s*\n(.*?)\n```"
    matches = re.findall(generic_block_pattern, text, re.DOTALL)
    for match in matches:
        if re.match(
            r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b",
            match,
            re.IGNORECASE,
        ):
            return match.strip()

    sql_pattern = (
        r"(?:^|\n)\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b.*?)(?=\n\n|\Z)"
    )
    matches = re.findall(sql_pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if matches:
        return matches[0].strip()

    return ""


def _first_sqlglot_error(exc: Exception) -> dict | None:
    errors = getattr(exc, "errors", None)
    if isinstance(errors, list) and errors:
        first = errors[0]
        return first if isinstance(first, dict) else None
    return None


def _format_error_location(exc: Exception) -> str | None:
    error = _first_sqlglot_error(exc)
    if error is None:
        return None

    line = error.get("line")
    column = error.get("col")
    parts = []
    if line is not None:
        parts.append(f"line {line}")
    if column is not None:
        parts.append(f"column {column}")
    return ", ".join(parts) or None


def _format_error_snippet(exc: Exception) -> str | None:
    error = _first_sqlglot_error(exc)
    if error is None:
        return None

    start_context = error.get("start_context") or ""
    highlight = error.get("highlight") or ""
    end_context = error.get("end_context") or ""
    snippet = f"{start_context}{highlight}{end_context}".strip()
    return snippet or None


def _build_potential_fix(problem: str, context: str) -> str:
    text = f"{problem} {context}".lower()
    if "expected table name" in text:
        return "Add the missing table name after the clause that references a table."
    if "expected" in text and "got" in text:
        return (
            "Check the SQL near the reported location for a missing keyword, identifier, "
            "comma, or closing delimiter."
        )
    if "unsupported" in text or "cannot" in text:
        return (
            "Choose a target dialect supported by sqlglot and avoid PostgreSQL-specific "
            "syntax that cannot be represented in the requested dialect."
        )
    if "unknown dialect" in text:
        return "Use a valid sqlglot dialect name such as `postgres`, `sqlite`, or `mysql`."
    return "Review the SQL syntax and the requested dialect, then try again."


def validate_postgres_sql(sql: str) -> None:
    if not sql.strip():
        raise ValueError(
            "SQL validation failed. "
            "\nProblem: Empty SQL input. "
            "\nContext: PostgreSQL validation requires at least one SQL statement. "
            "\nPotential fix: Provide one or more PostgreSQL statements to validate."
        ) from None

    try:
        sqlglot.parse(sql, read="postgres")
    except ParseError as exc:
        problem = (
            _first_sqlglot_error(exc) or {}
        ).get("description") or "The SQL text is not valid PostgreSQL syntax."
        context = "PostgreSQL parsing failed."
        location = _format_error_location(exc)
        snippet = _format_error_snippet(exc)

        error_parts = ["SQL validation failed."]
        if location:
            error_parts.append(f"\nLocation: {location}.")
        error_parts.append(f"\nProblem: {problem}.")
        error_parts.append(f"\nContext: {context}.")
        if snippet:
            error_parts.append(f"\nSnippet: {snippet}")
        error_parts.append(f"\nPotential fix: {_build_potential_fix(problem, context)}")
        raise ValueError(" ".join(error_parts)) from None
    except Exception as exc:
        raise ValueError(
            "Unexpected error while validating SQL: "
            f"{exc.__class__.__name__}: {exc}\n"
            "Potential fix: Check that the input is valid PostgreSQL SQL text and try again. "
            "If the problem persists, inspect custom SQL parser configuration."
        ) from None


def transpile_postgres_sql(sql: str, target_dialect: str) -> str:
    if not target_dialect.strip():
        raise ValueError(
            "SQL transpilation failed. "
            "\nProblem: Empty target dialect. "
            "\nContext: SQL transpilation requires a destination dialect name. "
            "\nPotential fix: Provide a sqlglot dialect name such as `sqlite`, `mysql`, or `duckdb`."
        ) from None

    validate_postgres_sql(sql)

    try:
        transpiled = sqlglot.transpile(
            sql,
            read="postgres",
            write=target_dialect,
            unsupported_level=sqlglot.ErrorLevel.RAISE,
        )
        return ";\n".join(statement.rstrip(";") for statement in transpiled if statement.strip())
    except (ParseError, UnsupportedError, ValueError) as exc:
        if isinstance(exc, ValueError):
            raise

        problem = (
            _first_sqlglot_error(exc) or {}
        ).get("description") or str(exc) or "SQL transpilation failed."
        context = f"Transpiling PostgreSQL SQL to `{target_dialect}` failed."
        location = _format_error_location(exc)
        snippet = _format_error_snippet(exc)

        error_parts = ["SQL transpilation failed."]
        if location:
            error_parts.append(f"\nLocation: {location}.")
        error_parts.append(f"\nProblem: {problem}.")
        error_parts.append(f"\nContext: {context}.")
        if snippet:
            error_parts.append(f"\nSnippet: {snippet}")
        error_parts.append(f"\nPotential fix: {_build_potential_fix(problem, context)}")
        raise ValueError(" ".join(error_parts)) from None
    except Exception as exc:
        raise ValueError(
            "Unexpected error while transpiling SQL: "
            f"{exc.__class__.__name__}: {exc}\n"
            "Potential fix: Check that the SQL is valid PostgreSQL and that the target dialect "
            "is supported by sqlglot."
        ) from None
