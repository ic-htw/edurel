import pytest
from textwrap import dedent
from edurel.utils.yaml import parse_yaml
from edurel.syntax.rel_yaml_schema import schema
from edurel.syntax.rel_ast import Column, DataList, ForeignKey, RelAstFactory, RelSchema, Table, enrich_ast, validate_ast


def test_parse_builds_rel_ast_from_valid_yaml() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
          - columnname: email
            type: TEXT
            nullable: true
          primary_key:
          - id
        - tablename: orders
          columns:
          - columnname: id
            type: INTEGER
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
        datalists:
        - tablename: order_status
          values:
          - pending
          - paid
        """
    )

    assert RelAstFactory.create_schema(parse_yaml(text, schema)) == RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="email", type="TEXT", nullable=True),
                ],
                primary_key=["id"],
            ),
            Table(
                tablename="orders",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="user_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        sourcecolumns=["user_id"],
                        targettable="users",
                        targetcolumns=["id"],
                    )
                ],
            ),
        ],
        datalists=[
            DataList(tablename="order_status", values=["pending", "paid"]),
        ],
    )


def test_parse_builds_rel_ast_when_primary_key_is_omitted() -> None:
    text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
        """
    )

    assert RelAstFactory.create_schema(parse_yaml(text, schema)) == RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=[],
            ),
        ]
    )


def test_validate_ast_accepts_valid_rel_schema() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="email", type="TEXT"),
                ],
                primary_key=["id"],
            ),
            Table(
                tablename="orders",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="user_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        fkname="fk_orders_users",
                        sourcecolumns=["user_id"],
                        targettable="users",
                        targetcolumns=["id"],
                    )
                ],
            ),
        ],
        datalists=[DataList(tablename="users", values=["alice", "bob"])],
    )

    assert validate_ast(rel_schema) is None


def test_validate_ast_reports_all_requested_semantic_errors() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="id", type="TEXT"),
                ],
                primary_key=["missing_pk"],
            ),
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="user_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        fkname="fk_dup",
                        sourcecolumns=["missing_source"],
                        targettable="missing_table",
                        targetcolumns=["id"],
                    ),
                    ForeignKey(
                        fkname="fk_dup",
                        sourcecolumns=["user_id"],
                        targettable="users",
                        targetcolumns=["not_a_target_pk"],
                    ),
                ],
            ),
        ],
        datalists=[
            DataList(tablename="users", values=["alice"]),
            DataList(tablename="users", values=["bob"]),
            DataList(tablename="missing_table", values=["ghost"]),
        ],
    )

    with pytest.raises(ValueError) as exc_info:
        validate_ast(rel_schema)

    message = str(exc_info.value)
    assert "AST validation failed:" in message
    assert "Duplicate table name 'users'." in message
    assert "Table 'users' has duplicate column name 'id'." in message
    assert "Table 'users' primary key 'missing_pk' is not a column." in message
    assert "Table 'users' has duplicate foreign key name 'fk_dup'." in message
    assert "references missing source column 'missing_source'" in message
    assert "references missing target table 'missing_table'" in message
    assert "references target column 'not_a_target_pk' that is not in primary key" in message
    assert "Duplicate datalist table name 'users'." in message
    assert "Datalist references missing table 'missing_table'." in message


def test_enrich_ast_assigns_levels_from_foreign_key_dependencies() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=["id"],
            ),
            Table(
                tablename="orders",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="user_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        sourcecolumns=["user_id"],
                        targettable="users",
                        targetcolumns=["id"],
                    )
                ],
            ),
            Table(
                tablename="order_items",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="order_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        sourcecolumns=["order_id"],
                        targettable="orders",
                        targetcolumns=["id"],
                    )
                ],
            ),
        ]
    )

    enrich_ast(rel_schema)

    levels = {table.tablename: table.level for table in rel_schema.tables}
    assert levels == {
        "users": 1,
        "orders": 2,
        "order_items": 3,
    }
    assert all(
        not foreign_key.is_cycle
        for table in rel_schema.tables
        for foreign_key in table.foreign_keys
    )


def test_enrich_ast_marks_cycle_foreign_keys_and_ignores_them_for_levels() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="profile_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        fkname="fk_users_profiles",
                        sourcecolumns=["profile_id"],
                        targettable="profiles",
                        targetcolumns=["id"],
                    )
                ],
            ),
            Table(
                tablename="profiles",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="owner_id", type="INTEGER"),
                ],
                primary_key=["id"],
                foreign_keys=[
                    ForeignKey(
                        fkname="fk_profiles_users",
                        sourcecolumns=["owner_id"],
                        targettable="users",
                        targetcolumns=["id"],
                    )
                ],
            ),
        ]
    )

    enrich_ast(rel_schema)

    tables_by_name = {table.tablename: table for table in rel_schema.tables}
    assert tables_by_name["profiles"].foreign_keys[0].is_cycle is True
    assert tables_by_name["users"].foreign_keys[0].is_cycle is False
    assert tables_by_name["users"].level == 2
    assert tables_by_name["profiles"].level == 1
