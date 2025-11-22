"""Tests for SQL to YAML transpiler."""

import pytest
from pathlib import Path
import yaml
from edurel.sql_to_yaml import sql_to_yaml


@pytest.fixture
def temp_sql_file(tmp_path):
    """Create a temporary SQL file for testing."""
    def _create_sql_file(content: str, filename: str = "test.sql"):
        sql_file = tmp_path / filename
        sql_file.write_text(content)
        return sql_file
    return _create_sql_file


def test_simple_table(temp_sql_file):
    """Test transpiling a simple table without constraints."""
    sql = """
    CREATE TABLE users (
        id INTEGER,
        username VARCHAR(50),
        email VARCHAR(100)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    assert 'tables' in data
    assert len(data['tables']) == 1

    table = data['tables'][0]
    assert table['name'] == 'users'
    assert len(table['columns']) == 3
    assert table['columns'][0]['name'] == 'id'


def test_table_with_constraints(temp_sql_file):
    """Test table with NOT NULL and other constraints."""
    sql = """
    CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    table = data['tables'][0]

    assert table['columns'][0]['constraints'] == 'NOT NULL'
    assert table['columns'][1]['constraints'] == 'NOT NULL'
    assert 'NOT NULL' in table['columns'][2]['constraints']
    assert 'UNIQUE' in table['columns'][2]['constraints']


def test_table_with_primary_key(temp_sql_file):
    """Test table with single primary key."""
    sql = """
    CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(50),
        PRIMARY KEY (id)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    table = data['tables'][0]

    assert 'primary_key' in table
    assert table['primary_key'] == ['id']


def test_table_with_compound_primary_key(temp_sql_file):
    """Test table with compound primary key."""
    sql = """
    CREATE TABLE user_roles (
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, role_id)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    table = data['tables'][0]

    assert 'primary_key' in table
    assert table['primary_key'] == ['user_id', 'role_id']


def test_table_with_foreign_key(temp_sql_file):
    """Test table with foreign key constraint."""
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50)
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    orders_table = next(t for t in data['tables'] if t['name'] == 'orders')

    assert 'foreign_keys' in orders_table
    assert len(orders_table['foreign_keys']) == 1

    fk = orders_table['foreign_keys'][0]
    assert fk['columns'] == ['user_id']
    assert fk['ref_table'] == 'users'
    assert fk['ref_columns'] == ['id']


def test_table_with_compound_foreign_key(temp_sql_file):
    """Test table with compound foreign key constraint."""
    sql = """
    CREATE TABLE users (
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        PRIMARY KEY (first_name, last_name)
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_first VARCHAR(50),
        user_last VARCHAR(50),
        FOREIGN KEY (user_first, user_last) REFERENCES users(first_name, last_name)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    orders_table = next(t for t in data['tables'] if t['name'] == 'orders')

    assert 'foreign_keys' in orders_table
    fk = orders_table['foreign_keys'][0]
    assert fk['columns'] == ['user_first', 'user_last']
    assert fk['ref_table'] == 'users'
    assert fk['ref_columns'] == ['first_name', 'last_name']


def test_alter_table_add_foreign_key(temp_sql_file):
    """Test ALTER TABLE ADD CONSTRAINT for foreign key."""
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50)
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL
    );

    ALTER TABLE orders
    ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id);
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    orders_table = next(t for t in data['tables'] if t['name'] == 'orders')

    assert 'foreign_keys' in orders_table
    assert len(orders_table['foreign_keys']) == 1

    fk = orders_table['foreign_keys'][0]
    assert fk['columns'] == ['user_id']
    assert fk['ref_table'] == 'users'
    assert fk['ref_columns'] == ['id']


def test_complex_schema(temp_sql_file):
    """Test complete schema with multiple tables and relationships."""
    sql = """
    CREATE TABLE users (
        id INTEGER NOT NULL,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        PRIMARY KEY (id)
    );

    CREATE TABLE orders (
        id INTEGER,
        user_id INTEGER NOT NULL,
        user_email VARCHAR(100) NOT NULL,
        order_date DATETIME NOT NULL,
        total DECIMAL(10,2),
        PRIMARY KEY (id)
    );

    ALTER TABLE orders
    ADD CONSTRAINT fk_users_user_id
    FOREIGN KEY (user_id) REFERENCES users(id);
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    assert len(data['tables']) == 2

    users_table = next(t for t in data['tables'] if t['name'] == 'users')
    assert users_table['primary_key'] == ['id']
    assert len(users_table['columns']) == 3

    orders_table = next(t for t in data['tables'] if t['name'] == 'orders')
    assert orders_table['primary_key'] == ['id']
    assert len(orders_table['columns']) == 5
    assert len(orders_table['foreign_keys']) == 1


def test_write_to_yaml_file(temp_sql_file, tmp_path):
    """Test writing output to YAML file."""
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50)
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_file = tmp_path / "output.yaml"

    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres", yaml_path=str(yaml_file))

    assert yaml_file.exists()
    content = yaml_file.read_text()
    assert content == yaml_output

    data = yaml.safe_load(content)
    assert 'tables' in data
    assert data['tables'][0]['name'] == 'users'


def test_file_not_found():
    """Test error handling for non-existent SQL file."""
    with pytest.raises(FileNotFoundError):
        sql_to_yaml("nonexistent.sql", dialect="postgres")


def test_multiple_tables(temp_sql_file):
    """Test transpiling multiple tables."""
    sql = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY
    );
    """
    sql_file = temp_sql_file(sql)
    yaml_output = sql_to_yaml(str(sql_file), dialect="postgres")

    data = yaml.safe_load(yaml_output)
    assert len(data['tables']) == 3
    table_names = [t['name'] for t in data['tables']]
    assert 'users' in table_names
    assert 'products' in table_names
    assert 'orders' in table_names
