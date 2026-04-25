from edurel.syntax.rel_ast import Column, DataList, ForeignKey, RelSchema, Table
from edurel.translation.rel_trans import (
    RelSchemaLevelTranslationVisitor,
    RelSchemaTranslationBuilder,
    RelSchemaTranslationVisitor,
    SqlTranslationBuilderFkExternal,
    SqlTranslationBuilderFkInternal,
)


class RecordingBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.events: list[str] = []

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.events.append("start_schema")

    def end_schema(self, rel_schema: RelSchema) -> None:
        self.events.append("end_schema")

    def start_table(self, table: Table) -> None:
        self.events.append(f"start_table:{table.tablename}")

    def add_column(self, table: Table, column: Column) -> None:
        self.events.append(f"column:{table.tablename}.{column.columnname}")

    def add_primary_key(self, table: Table) -> None:
        self.events.append(f"primary_key:{table.tablename}")

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        self.events.append(f"foreign_key:{table.tablename}->{foreign_key.targettable}")

    def end_table(self, table: Table) -> None:
        self.events.append(f"end_table:{table.tablename}")

    def add_datalist(self, datalist: DataList) -> None:
        self.events.append(f"datalist:{datalist.tablename}")

    def build(self) -> str:
        return "\n".join(self.events)


def test_level_translation_visitor_traverses_tables_in_level_order() -> None:
    rel_schema = RelSchema(
        tables=[
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
                level=2,
            ),
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=["id"],
                level=1,
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
                level=3,
            ),
        ],
        datalists=[DataList(tablename="users", values=["alice"])],
    )

    builder = RecordingBuilder()
    visitor = RelSchemaLevelTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.events == [
        "start_schema",
        "start_table:users",
        "column:users.id",
        "primary_key:users",
        "end_table:users",
        "start_table:orders",
        "column:orders.id",
        "column:orders.user_id",
        "primary_key:orders",
        "foreign_key:orders->users",
        "end_table:orders",
        "start_table:order_items",
        "column:order_items.id",
        "column:order_items.order_id",
        "primary_key:order_items",
        "foreign_key:order_items->orders",
        "end_table:order_items",
        "datalist:users",
        "end_schema",
    ]


def test_level_translation_visitor_does_nothing_when_all_table_levels_are_zero() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="users",
                columns=[Column(columnname="id", type="INTEGER")],
                primary_key=["id"],
            )
        ],
        datalists=[DataList(tablename="users", values=["alice"])],
    )

    builder = RecordingBuilder()
    visitor = RelSchemaLevelTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.events == []


def test_sql_translation_builder_fk_internal_inlines_foreign_keys_in_create_table() -> None:
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

    builder = SqlTranslationBuilderFkInternal()
    visitor = RelSchemaTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.build() == (
        "CREATE TABLE users (\n"
        "  id INTEGER NOT NULL,\n"
        "  PRIMARY KEY (id)\n"
        ");\n"
        "CREATE TABLE orders (\n"
        "  id INTEGER NOT NULL,\n"
        "  user_id INTEGER NOT NULL,\n"
        "  PRIMARY KEY (id),\n"
        "  CONSTRAINT fk_orders_users FOREIGN KEY (user_id) REFERENCES users (id)\n"
        ");"
    )


def test_sql_translation_builder_fk_internal_comments_out_cycle_foreign_keys() -> None:
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
                        is_cycle=True,
                    )
                ],
            )
        ]
    )

    builder = SqlTranslationBuilderFkInternal()
    visitor = RelSchemaTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.build() == (
        "CREATE TABLE users (\n"
        "  id INTEGER NOT NULL,\n"
        "  profile_id INTEGER NOT NULL,\n"
        "  PRIMARY KEY (id)\n"
        "  -- CONSTRAINT fk_users_profiles FOREIGN KEY (profile_id) REFERENCES profiles (id)\n"
        ");"
    )


def test_sql_translation_builder_fk_external_generates_datalist_insert_statements() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="status_codes",
                columns=[
                    Column(columnname="ID", type="INTEGER"),
                    Column(columnname="Description", type="VARCHAR(255)"),
                    Column(columnname="IsValid", type="BOOLEAN"),
                    Column(columnname="SortOrder", type="INTEGER"),
                ],
                primary_key=["ID"],
            )
        ],
        datalists=[DataList(tablename="status_codes", values=["Open", "Closed", "Owner's Review"])],
    )

    builder = SqlTranslationBuilderFkExternal()
    visitor = RelSchemaTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.build() == (
        "CREATE TABLE status_codes (\n"
        "  ID INTEGER NOT NULL,\n"
        "  Description VARCHAR(255) NOT NULL,\n"
        "  IsValid BOOLEAN NOT NULL,\n"
        "  SortOrder INTEGER NOT NULL,\n"
        "  PRIMARY KEY (ID)\n"
        ");\n"
        "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) VALUES (1, 'Open', 1, 1);\n"
        "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) VALUES (2, 'Closed', 1, 2);\n"
        "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) VALUES (3, 'Owner''s Review', 1, 3);"
    )


def test_sql_translation_builder_fk_internal_generates_datalist_insert_statements() -> None:
    rel_schema = RelSchema(
        tables=[
            Table(
                tablename="status_codes",
                columns=[
                    Column(columnname="ID", type="INTEGER"),
                    Column(columnname="Description", type="VARCHAR(255)"),
                    Column(columnname="IsValid", type="BOOLEAN"),
                    Column(columnname="SortOrder", type="INTEGER"),
                ],
                primary_key=["ID"],
            )
        ],
        datalists=[DataList(tablename="status_codes", values=["Open", "Closed"])],
    )

    builder = SqlTranslationBuilderFkInternal()
    visitor = RelSchemaTranslationVisitor(builder)

    visitor.visit(rel_schema)

    assert builder.build() == (
        "CREATE TABLE status_codes (\n"
        "  ID INTEGER NOT NULL,\n"
        "  Description VARCHAR(255) NOT NULL,\n"
        "  IsValid BOOLEAN NOT NULL,\n"
        "  SortOrder INTEGER NOT NULL,\n"
        "  PRIMARY KEY (ID)\n"
        ");\n"
        "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) VALUES (1, 'Open', 1, 1);\n"
        "INSERT INTO status_codes (ID, Description, IsValid, SortOrder) VALUES (2, 'Closed', 1, 2);"
    )
