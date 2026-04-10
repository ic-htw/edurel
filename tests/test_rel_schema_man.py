from textwrap import dedent

from edurel.core.rel_schema_man import RelSchemaMan
from edurel.syntax.rel_ast import Column, DataList, ForeignKey, RelSchema, Table
from edurel.syntax.rel_yaml_schema import schema
from edurel.utils.yaml import parse_yaml


def test_get_yaml_serializes_ast_to_valid_canonical_yaml() -> None:
    rel_schema = RelSchema(
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

    yaml_text = RelSchemaMan.fromAST(rel_schema).get_yaml()

    assert parse_yaml(yaml_text, schema) == {
        "tables": [
            {
                "tablename": "users",
                "columns": [
                    {"columnname": "id", "type": "INTEGER"},
                    {"columnname": "email", "type": "TEXT", "nullable": True},
                ],
                "primary_key": ["id"],
            },
            {
                "tablename": "orders",
                "columns": [
                    {"columnname": "id", "type": "INTEGER"},
                    {"columnname": "user_id", "type": "INTEGER"},
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
        "datalists": [{"tablename": "users", "values": ["alice", "bob"]}],
    }


def test_from_url_reads_yaml_from_url() -> None:
    yaml_text = dedent(
        """
        tables:
        - tablename: users
          columns:
          - columnname: id
            type: INTEGER
          primary_key:
          - id
        """
    ).strip()

    class FakeHeaders:
        def get_content_charset(self) -> str:
            return "utf-8"

    class FakeResponse:
        def __init__(self, body: str):
            self.body = body.encode("utf-8")
            self.headers = FakeHeaders()

        def read(self) -> bytes:
            return self.body

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    calls: list[str] = []

    def fake_urlopen(url: str) -> FakeResponse:
        calls.append(url)
        return FakeResponse(yaml_text)

    import edurel.core.rel_schema_man as rel_schema_man_module

    original_urlopen = rel_schema_man_module.urlopen
    rel_schema_man_module.urlopen = fake_urlopen
    try:
        rel_schema_man = RelSchemaMan.fromURL("https://example.com/schema.yaml")
    finally:
        rel_schema_man_module.urlopen = original_urlopen

    assert calls == ["https://example.com/schema.yaml"]
    assert rel_schema_man.get_ast() == RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=["id"],
            )
        ]
    )


def test_get_sql_generates_foreign_keys_in_alter_table_statements() -> None:
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
                        fkname="fk_orders_users",
                        sourcecolumns=["user_id"],
                        targettable="users",
                        targetcolumns=["id"],
                    )
                ],
            ),
        ]
    )

    assert RelSchemaMan.fromAST(rel_schema).get_sql() == dedent(
        """
        CREATE TABLE users (
          id INTEGER NOT NULL,
          PRIMARY KEY (id)
        );
        CREATE TABLE orders (
          id INTEGER NOT NULL,
          user_id INTEGER NOT NULL,
          PRIMARY KEY (id)
        );
        ALTER TABLE orders
          ADD CONSTRAINT fk_orders_users FOREIGN KEY (user_id) REFERENCES users (id);
        """
    ).strip()


def test_get_mermaid_uses_requested_fk_connectors_and_strips_type_sizes() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="balance", type="DECIMAL(9, 2)", nullable=True),
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
            Table(
                tablename="draft_orders",
                columns=[
                    Column(columnname="id", type="INTEGER"),
                    Column(columnname="user_id", type="INTEGER", nullable=True),
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
        ]
    )

    assert RelSchemaMan.fromAST(rel_schema).get_mermaid_code() == dedent(
        """
        erDiagram
          direction TB
          users {
            INTEGER id PK
            DECIMAL balance
          }
          orders {
            INTEGER id PK
            INTEGER user_id FK
          }
          draft_orders {
            INTEGER id PK
            INTEGER user_id FK
          }
          orders }|--o| users : "user_id -> id"
          draft_orders }o--o| users : "user_id -> id"
        """
    ).strip()


def test_get_mermaid_code_includes_requested_direction() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=["id"],
            )
        ]
    )

    assert RelSchemaMan.fromAST(rel_schema).get_mermaid_code(direction="LR") == dedent(
        """
        erDiagram
          direction LR
          users {
            INTEGER id PK
          }
        """
    ).strip()


def test_get_structure_emits_compact_prompt_friendly_lines() -> None:
    rel_schema = RelSchema(
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
        ]
    )

    assert RelSchemaMan.fromAST(rel_schema).get_structure() == dedent(
        """
        - table: users(id, email)
        - table: orders(id, user_id)
        - fk: orders(user_id)->users(id)
        """
    ).strip()
