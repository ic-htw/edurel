import pytest
from edurel.utils.misc import sql_extract


class TestSqlExtract:
    """Test suite for sql_extract function."""

    def test_markdown_sql_block(self):
        """Test extraction from markdown sql code block."""
        text = """
Here is some SQL:

```sql
SELECT * FROM users WHERE id = 1
```

That was the query.
"""
        result = sql_extract(text)
        assert result == "SELECT * FROM users WHERE id = 1"

    def test_markdown_sql_block_case_insensitive(self):
        """Test extraction from markdown SQL code block (uppercase)."""
        text = """
```SQL
SELECT name, email FROM customers
```
"""
        result = sql_extract(text)
        assert result == "SELECT name, email FROM customers"

    def test_markdown_generic_block_with_sql(self):
        """Test extraction from generic markdown block containing SQL."""
        text = """
Here's a query:

```
SELECT id, name
FROM products
WHERE price > 100
```
"""
        result = sql_extract(text)
        assert result == "SELECT id, name\nFROM products\nWHERE price > 100"

    def test_markdown_generic_block_without_sql(self):
        """Test that non-SQL generic blocks are ignored."""
        text = """
```
This is just some text
not a SQL query
```
"""
        result = sql_extract(text)
        assert result == ""

    def test_plain_text_select(self):
        """Test extraction of SELECT from plain text."""
        text = """
The query we need is:
SELECT * FROM orders WHERE status = 'pending'

And that should work fine.
"""
        result = sql_extract(text)
        assert result == "SELECT * FROM orders WHERE status = 'pending'"

    def test_plain_text_insert(self):
        """Test extraction of INSERT from plain text."""
        text = "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
        result = sql_extract(text)
        assert result == "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"

    def test_plain_text_update(self):
        """Test extraction of UPDATE from plain text."""
        text = "UPDATE products SET price = 99.99 WHERE id = 5"
        result = sql_extract(text)
        assert result == "UPDATE products SET price = 99.99 WHERE id = 5"

    def test_plain_text_delete(self):
        """Test extraction of DELETE from plain text."""
        text = "DELETE FROM logs WHERE created_at < '2020-01-01'"
        result = sql_extract(text)
        assert result == "DELETE FROM logs WHERE created_at < '2020-01-01'"

    def test_plain_text_create(self):
        """Test extraction of CREATE from plain text."""
        text = "CREATE TABLE employees (id INTEGER, name TEXT)"
        result = sql_extract(text)
        assert result == "CREATE TABLE employees (id INTEGER, name TEXT)"

    def test_plain_text_drop(self):
        """Test extraction of DROP from plain text."""
        text = "DROP TABLE temp_table"
        result = sql_extract(text)
        assert result == "DROP TABLE temp_table"

    def test_plain_text_alter(self):
        """Test extraction of ALTER from plain text."""
        text = "ALTER TABLE users ADD COLUMN age INTEGER"
        result = sql_extract(text)
        assert result == "ALTER TABLE users ADD COLUMN age INTEGER"

    def test_plain_text_with_cte(self):
        """Test extraction of WITH (CTE) from plain text."""
        text = """
WITH top_customers AS (
    SELECT customer_id, SUM(amount) as total
    FROM orders
    GROUP BY customer_id
)
SELECT * FROM top_customers
"""
        result = sql_extract(text)
        assert "WITH top_customers AS" in result
        assert "SELECT * FROM top_customers" in result

    def test_multiline_sql_in_markdown(self):
        """Test extraction of multiline SQL from markdown."""
        text = """
```sql
SELECT
    u.id,
    u.name,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
```
"""
        result = sql_extract(text)
        assert "SELECT" in result
        assert "FROM users u" in result
        assert "GROUP BY u.id, u.name" in result
        assert "HAVING COUNT(o.id) > 5" in result

    def test_no_sql_found(self):
        """Test that empty string is returned when no SQL is found."""
        text = "This is just regular text with no SQL statements."
        result = sql_extract(text)
        assert result == ""

    def test_empty_string(self):
        """Test with empty string input."""
        result = sql_extract("")
        assert result == ""

    def test_sql_with_leading_whitespace(self):
        """Test SQL extraction with leading whitespace."""
        text = """
```sql
   SELECT * FROM users
```
"""
        result = sql_extract(text)
        assert result == "SELECT * FROM users"

    def test_multiple_sql_blocks_returns_first(self):
        """Test that only the first SQL block is returned."""
        text = """
```sql
SELECT * FROM users
```

Some text in between.

```sql
SELECT * FROM orders
```
"""
        result = sql_extract(text)
        assert result == "SELECT * FROM users"

    def test_case_insensitive_keywords_in_plain_text(self):
        """Test case insensitive keyword matching in plain text."""
        text = "select id, name from users where active = true"
        result = sql_extract(text)
        assert result == "select id, name from users where active = true"

    def test_sql_followed_by_double_newline(self):
        """Test SQL extraction stops at double newline."""
        text = """
SELECT * FROM users

This is additional text that should not be included.
"""
        result = sql_extract(text)
        assert result == "SELECT * FROM users"
        assert "This is additional text" not in result
