import pytest
from edurel.utils.misc import sql_extract, gslice


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


class TestGslice:
    """Test suite for gslice function."""

    def test_single_index(self):
        """Test selecting a single element by index."""
        f = gslice("2")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['c']

    def test_multiple_indices(self):
        """Test selecting multiple individual elements."""
        f = gslice("0, 2, 4")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['a', 'c', 'e']

    def test_single_range(self):
        """Test selecting a range of elements."""
        f = gslice("1:4")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['b', 'c', 'd']

    def test_multiple_ranges(self):
        """Test selecting multiple ranges."""
        f = gslice("0:2, 3:5")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['a', 'b', 'd', 'e']

    def test_mixed_indices_and_ranges(self):
        """Test mixing individual indices and ranges."""
        f = gslice("0, 2:5, 7")
        result = f(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        assert result == ['a', 'c', 'd', 'e', 'h']

    def test_negative_index(self):
        """Test using negative indices."""
        f = gslice("-1")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['e']

    def test_negative_indices_multiple(self):
        """Test using multiple negative indices."""
        f = gslice("-3, -1")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['c', 'e']

    def test_negative_range(self):
        """Test using negative indices in ranges."""
        f = gslice("-3:-1")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['c', 'd']

    def test_mixed_positive_negative(self):
        """Test mixing positive and negative indices."""
        f = gslice("1:3, -1")
        result = f([10, 20, 30, 40, 50])
        assert result == [20, 30, 50]

    def test_open_start_range(self):
        """Test range with open start (from beginning)."""
        f = gslice(":3")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['a', 'b', 'c']

    def test_open_end_range(self):
        """Test range with open end (to end of list)."""
        f = gslice("2:")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['c', 'd', 'e']

    def test_open_both_range(self):
        """Test range with both ends open (entire list)."""
        f = gslice(":")
        result = f(['a', 'b', 'c'])
        assert result == ['a', 'b', 'c']

    def test_multiple_open_ranges(self):
        """Test multiple ranges with open ends."""
        f = gslice(":2, -2:")
        result = f(['x', 'y', 'z', 'w'])
        assert result == ['x', 'y', 'z', 'w']

    def test_empty_list(self):
        """Test with empty list."""
        f = gslice(":")
        result = f([])
        assert result == []

    def test_single_element_list(self):
        """Test with single element list."""
        f = gslice("0")
        result = f(['x'])
        assert result == ['x']

    def test_out_of_order_indices(self):
        """Test that indices are returned in spec order, not list order."""
        f = gslice("4, 1, 3")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['e', 'b', 'd']

    def test_overlapping_ranges(self):
        """Test with overlapping ranges."""
        f = gslice("0:3, 1:4")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == ['a', 'b', 'c', 'b', 'c', 'd']

    def test_duplicate_indices(self):
        """Test with duplicate indices."""
        f = gslice("1, 1, 1")
        result = f(['a', 'b', 'c'])
        assert result == ['b', 'b', 'b']

    def test_whitespace_handling(self):
        """Test that whitespace in spec is handled correctly."""
        f = gslice(" 0 , 2:4 , 5 ")
        result = f(['a', 'b', 'c', 'd', 'e', 'f'])
        assert result == ['a', 'c', 'd', 'f']

    def test_empty_range(self):
        """Test range that selects no elements."""
        f = gslice("3:3")
        result = f(['a', 'b', 'c', 'd', 'e'])
        assert result == []

    def test_numeric_list(self):
        """Test with numeric list."""
        f = gslice("0, 2:4")
        result = f([10, 20, 30, 40, 50])
        assert result == [10, 30, 40]

    def test_complex_spec(self):
        """Test complex spec with multiple operations."""
        f = gslice("0, 2:5, 7, 9:11, -1")
        result = f([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        assert result == [0, 2, 3, 4, 7, 9, 10, 11]

    def test_function_reusability(self):
        """Test that returned function can be reused on different lists."""
        f = gslice("0, -1")
        result1 = f(['a', 'b', 'c'])
        result2 = f([1, 2, 3, 4, 5])
        assert result1 == ['a', 'c']
        assert result2 == [1, 5]
