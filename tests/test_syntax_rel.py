import pytest
from textwrap import dedent
from edurel.utils.yaml import parse_yaml
from edurel.syntax.rel_yaml_schema import schema

def test_parse_yaml_accepts_complete_valid_document() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
            nullable: false
          - columnname: balance
            type: DECIMAL(9,2)
            nullable: true
          primary_key:
          - id
        - tablename: orders
          columns:
          - columnname: id
            type: INTEGER
            nullable: false
          - columnname: user_id
            type: INTEGER
            nullable: false
          primary_key:
          - id
          foreign_keys:
          - fkname: fk_orders_users
            sourcecolumns:
            - user_id
            targettable: users
            targetcolumns:
            - id
        datalists:
        - tablename: order_status
          values:
          - pending
          - paid
        """
    )

    assert parse_yaml(text, schema) == {
        "tables": [
            {
                "tablename": "users",
                "columns": [
                    {"columnname": "id", "type": "INTEGER", "nullable": False},
                    {
                        "columnname": "balance",
                        "type": "DECIMAL(9,2)",
                        "nullable": True,
                    },
                ],
                "primary_key": ["id"],
            },
            {
                "tablename": "orders",
                "columns": [
                    {"columnname": "id", "type": "INTEGER", "nullable": False},
                    {"columnname": "user_id", "type": "INTEGER", "nullable": False},
                ],
                "primary_key": ["id"],
                "foreign_keys": [
                    {
                        "fkname": "fk_orders_users",
                        "sourcecolumns": ["user_id"],
                        "targettable": "users",
                        "targetcolumns": ["id"],
                    }
                ],
            },
        ],
        "datalists": [
            {
                "tablename": "order_status",
                "values": ["pending", "paid"],
            }
        ],
    }


def test_parse_yaml_allows_omitted_nullable_and_fkname() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
          - columnname: balance
            type: DECIMAL(9,2)
            nullable: true
          primary_key:
          - id
        - tablename: orders
          columns:
          - columnname: id
            type: INTEGER
            nullable: false
          - columnname: user_id
            type: INTEGER
          primary_key:
          - id
          foreign_keys:
          - sourcecolumns:
            - user_id
            targettable: users
            targetcolumns:
            - id
        """
    )

    assert parse_yaml(text, schema) == {
        "tables": [
            {
                "tablename": "users",
                "columns": [
                    {"columnname": "id", "type": "INTEGER"},
                    {
                        "columnname": "balance",
                        "type": "DECIMAL(9,2)",
                        "nullable": True,
                    },
                ],
                "primary_key": ["id"],
            },
            {
                "tablename": "orders",
                "columns": [
                    {"columnname": "id", "type": "INTEGER", "nullable": False},
                    {"columnname": "user_id", "type": "INTEGER"},
                ],
                "primary_key": ["id"],
                "foreign_keys": [
                    {
                        "sourcecolumns": ["user_id"],
                        "targettable": "users",
                        "targetcolumns": ["id"],
                    }
                ],
            },
        ]
    }


def test_parse_yaml_allows_omitted_optional_sections() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
          primary_key:
          - id
        """
    )

    assert parse_yaml(text, schema) == {
        "tables": [
            {
                "tablename": "users",
                "columns": [{"columnname": "id", "type": "INTEGER"}],
                "primary_key": ["id"],
            }
        ]
    }


@pytest.mark.parametrize(
    "sql_type",
    [
        "DECIMAL(9, 2)",
        "DECIMAL( 9,2)",
        "DECIMAL(9 , 2 )",
    ],
)
def test_parse_yaml_accepts_sql_type_values_with_spaces(sql_type: str) -> None:
    text = dedent(
        f"""
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: {sql_type}
          primary_key:
          - id
        """
    )

    assert parse_yaml(text, schema) == {
        "tables": [
            {
                "tablename": "users",
                "columns": [{"columnname": "id", "type": sql_type}],
                "primary_key": ["id"],
            }
        ]
    }


@pytest.mark.parametrize(
    "sql_type",
    [
        "INTEGER()",
        "VARCHAR(abc)",
        "TEXT()",
        "DECIMAL(9,2,1)",
    ],
)
def test_parse_yaml_rejects_invalid_sql_type_values(sql_type: str) -> None:
    text = dedent(
        f"""
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: {sql_type}
            nullable: false
          primary_key:
          - id
        """
    )

    with pytest.raises(ValueError, match="YAML validation failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "found non-matching string" in message or "when expecting string matching" in message
    assert "Check the field format against the schema." in message


def test_parse_yaml_reports_schema_error_with_fix() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            nullable: false
          primary_key:
          - id
        """
    )

    with pytest.raises(ValueError, match="YAML validation failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "line 5, column 1" in message
    assert "required key(s) 'type' not found" in message
    assert "Add the missing required field" in message
    assert "`columnname` and `type`" in message


def test_parse_yaml_reports_malformed_yaml_with_fix() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
            - columnname: id
             type: INTEGER
        """
    )

    with pytest.raises(ValueError, match="YAML parsing failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "line 6, column 6" in message
    assert "expected <block end>" in message
    assert "indentation" in message


