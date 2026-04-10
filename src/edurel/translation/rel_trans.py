from abc import ABC, abstractmethod
import re

from edurel.syntax.rel_ast import Column, DataList, ForeignKey, RelSchema, Table


class RelSchemaTranslationBuilder(ABC):
    @abstractmethod
    def start_schema(self, rel_schema: RelSchema) -> None:
        pass

    @abstractmethod
    def end_schema(self, rel_schema: RelSchema) -> None:
        pass

    @abstractmethod
    def start_table(self, table: Table) -> None:
        pass

    @abstractmethod
    def add_column(self, table: Table, column: Column) -> None:
        pass

    @abstractmethod
    def add_primary_key(self, table: Table) -> None:
        pass

    @abstractmethod
    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        pass

    @abstractmethod
    def end_table(self, table: Table) -> None:
        pass

    @abstractmethod
    def add_datalist(self, datalist: DataList) -> None:
        pass

    @abstractmethod
    def build(self) -> str:
        pass


class RelSchemaTranslationVisitor:
    def __init__(self, builder: RelSchemaTranslationBuilder):
        self.builder = builder

    def visit(self, node: RelSchema | Table | DataList) -> None:
        visit_method = getattr(self, f"visit_{type(node).__name__}")
        visit_method(node)

    def visit_RelSchema(self, rel_schema: RelSchema) -> None:
        self.builder.start_schema(rel_schema)
        for table in rel_schema.tables:
            self.visit(table)
        for datalist in rel_schema.datalists:
            self.visit(datalist)
        self.builder.end_schema(rel_schema)

    def visit_Table(self, table: Table) -> None:
        self.builder.start_table(table)
        for column in table.columns:
            self.builder.add_column(table, column)
        self.builder.add_primary_key(table)
        for foreign_key in table.foreign_keys:
            self.builder.add_foreign_key(table, foreign_key)
        self.builder.end_table(table)

    def visit_DataList(self, datalist: DataList) -> None:
        self.builder.add_datalist(datalist)


class RelSchemaLevelTranslationVisitor(RelSchemaTranslationVisitor):
    def visit_RelSchema(self, rel_schema: RelSchema) -> None:
        if not rel_schema.tables or all(table.level == 0 for table in rel_schema.tables):
            return

        self.builder.start_schema(rel_schema)
        leveled_tables = [table for table in rel_schema.tables if table.level > 0]
        for table in sorted(leveled_tables, key=lambda table: table.level):
            self.visit(table)
        for datalist in rel_schema.datalists:
            self.visit(datalist)
        self.builder.end_schema(rel_schema)


def _yaml_scalar(value: str | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value == "" or value.lower() in {"true", "false", "null", "~"}:
        return "'" + value.replace("'", "''") + "'"
    if re.fullmatch(r"[A-Za-z0-9_(), .-]+", value):
        return value
    return "'" + value.replace("'", "''") + "'"


def _strip_sql_type_size(sql_type: str) -> str:
    return re.sub(r"\s*\(.*\)$", "", sql_type).strip()


def _sql_foreign_key_constraint(foreign_key: ForeignKey) -> str:
    constraint_sql = ""
    if foreign_key.fkname:
        constraint_sql += f"CONSTRAINT {foreign_key.fkname} "
    constraint_sql += (
        f"FOREIGN KEY ({', '.join(foreign_key.sourcecolumns)}) "
        f"REFERENCES {foreign_key.targettable} ({', '.join(foreign_key.targetcolumns)})"
    )
    return constraint_sql


def _sql_string_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _sql_datalist_insert_statements(datalist: DataList) -> list[str]:
    statements: list[str] = []
    for index, value in enumerate(datalist.values, start=1):
        statements.append(
            f"INSERT INTO {datalist.tablename} (ID, Description, IsValid, SortOrder) "
            f"VALUES ({index}, {_sql_string_literal(value)}, TRUE, {index});"
        )
    return statements


class YamlTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.tables: list[dict] = []
        self.datalists: list[dict] = []
        self.current_table: dict | None = None

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.tables = []
        self.datalists = []

    def end_schema(self, rel_schema: RelSchema) -> None:
        return None

    def start_table(self, table: Table) -> None:
        self.current_table = {
            "tablename": table.tablename,
            "columns": [],
            "primary_key": [],
        }

    def add_column(self, table: Table, column: Column) -> None:
        assert self.current_table is not None
        column_dict = {
            "columnname": column.columnname,
            "type": column.type,
        }
        if column.nullable:
            column_dict["nullable"] = True
        self.current_table["columns"].append(column_dict)

    def add_primary_key(self, table: Table) -> None:
        assert self.current_table is not None
        self.current_table["primary_key"] = list(table.primary_key)

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        assert self.current_table is not None
        foreign_key_dict = {
            "sourcecolumns": list(foreign_key.sourcecolumns),
            "targettable": foreign_key.targettable,
            "targetcolumns": list(foreign_key.targetcolumns),
        }
        if foreign_key.fkname:
            foreign_key_dict["fkname"] = foreign_key.fkname
        self.current_table.setdefault("foreign_keys", []).append(foreign_key_dict)

    def end_table(self, table: Table) -> None:
        assert self.current_table is not None
        self.tables.append(self.current_table)
        self.current_table = None

    def add_datalist(self, datalist: DataList) -> None:
        self.datalists.append(
            {
                "tablename": datalist.tablename,
                "values": list(datalist.values),
            }
        )

    def build(self) -> str:
        lines: list[str] = ["tables:"]
        for table in self.tables:
            lines.append(f"- tablename: {_yaml_scalar(table['tablename'])}")
            lines.append("  columns:")
            for column in table["columns"]:
                lines.append(f"  - columnname: {_yaml_scalar(column['columnname'])}")
                lines.append(f"    type: {_yaml_scalar(column['type'])}")
                if column.get("nullable"):
                    lines.append("    nullable: true")
            lines.append("  primary_key:")
            for primary_key in table["primary_key"]:
                lines.append(f"  - {_yaml_scalar(primary_key)}")
            foreign_keys = table.get("foreign_keys", [])
            if foreign_keys:
                lines.append("  foreign_keys:")
                for foreign_key in foreign_keys:
                    lines.append("  -")
                    if foreign_key.get("fkname"):
                        lines.append(f"    fkname: {_yaml_scalar(foreign_key['fkname'])}")
                    lines.append("    sourcecolumns:")
                    for source_column in foreign_key["sourcecolumns"]:
                        lines.append(f"    - {_yaml_scalar(source_column)}")
                    lines.append(f"    targettable: {_yaml_scalar(foreign_key['targettable'])}")
                    lines.append("    targetcolumns:")
                    for target_column in foreign_key["targetcolumns"]:
                        lines.append(f"    - {_yaml_scalar(target_column)}")
        if self.datalists:
            lines.append("datalists:")
            for datalist in self.datalists:
                lines.append(f"- tablename: {_yaml_scalar(datalist['tablename'])}")
                lines.append("  values:")
                for value in datalist["values"]:
                    lines.append(f"  - {_yaml_scalar(value)}")
        return "\n".join(lines)


class SqlTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.create_statements: list[str] = []
        self.alter_statements: list[str] = []
        self.insert_statements: list[str] = []
        self.current_table_lines: list[str] = []

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.create_statements = []
        self.alter_statements = []
        self.insert_statements = []

    def end_schema(self, rel_schema: RelSchema) -> None:
        return None

    def start_table(self, table: Table) -> None:
        self.current_table_lines = []

    def add_column(self, table: Table, column: Column) -> None:
        column_sql = f"  {column.columnname} {column.type}"
        if not column.nullable:
            column_sql += " NOT NULL"
        self.current_table_lines.append(column_sql)

    def add_primary_key(self, table: Table) -> None:
        self.current_table_lines.append(f"  PRIMARY KEY ({', '.join(table.primary_key)})")

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        constraint_sql = (
            f"ALTER TABLE {table.tablename}\n"
            f"  ADD {_sql_foreign_key_constraint(foreign_key)};"
        )
        self.alter_statements.append(constraint_sql)

    def end_table(self, table: Table) -> None:
        body = ",\n".join(self.current_table_lines)
        self.create_statements.append(f"CREATE TABLE {table.tablename} (\n{body}\n);")

    def add_datalist(self, datalist: DataList) -> None:
        self.insert_statements.extend(_sql_datalist_insert_statements(datalist))

    def build(self) -> str:
        statements = list(self.create_statements)
        statements.extend(self.alter_statements)
        statements.extend(self.insert_statements)
        return "\n".join(statements)


class SqlInlineTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.create_statements: list[str] = []
        self.insert_statements: list[str] = []
        self.current_table_lines: list[str] = []
        self.current_table_comments: list[str] = []

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.create_statements = []
        self.insert_statements = []

    def end_schema(self, rel_schema: RelSchema) -> None:
        return None

    def start_table(self, table: Table) -> None:
        self.current_table_lines = []
        self.current_table_comments = []

    def add_column(self, table: Table, column: Column) -> None:
        column_sql = f"  {column.columnname} {column.type}"
        if not column.nullable:
            column_sql += " NOT NULL"
        self.current_table_lines.append(column_sql)

    def add_primary_key(self, table: Table) -> None:
        self.current_table_lines.append(f"  PRIMARY KEY ({', '.join(table.primary_key)})")

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        constraint_sql = f"  {_sql_foreign_key_constraint(foreign_key)}"
        if foreign_key.is_cycle:
            self.current_table_comments.append(f"  -- {constraint_sql.strip()}")
            return
        self.current_table_lines.append(constraint_sql)

    def end_table(self, table: Table) -> None:
        body_lines = [",\n".join(self.current_table_lines)]
        if self.current_table_comments:
            body_lines.extend(self.current_table_comments)
        body = "\n".join(line for line in body_lines if line)
        self.create_statements.append(f"CREATE TABLE {table.tablename} (\n{body}\n);")

    def add_datalist(self, datalist: DataList) -> None:
        self.insert_statements.extend(_sql_datalist_insert_statements(datalist))

    def build(self) -> str:
        statements = list(self.create_statements)
        statements.extend(self.insert_statements)
        return "\n".join(statements)


class MermaidTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self, direction: str = "TB") -> None:
        self.direction = direction
        self.lines: list[str] = []
        self.relationships: list[str] = []
        self.table_columns: dict[str, list[str]] = {}
        self.table_column_lookup: dict[str, dict[str, Column]] = {}

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.lines = ["erDiagram", f"  direction {self.direction}"]
        self.relationships = []
        self.table_columns = {}
        self.table_column_lookup = {
            table.tablename: {column.columnname: column for column in table.columns}
            for table in rel_schema.tables
        }

    def end_schema(self, rel_schema: RelSchema) -> None:
        for table in rel_schema.tables:
            self.lines.append(f"  {table.tablename} {{")
            self.lines.extend(self.table_columns.get(table.tablename, []))
            self.lines.append("  }")
        self.lines.extend(self.relationships)

    def start_table(self, table: Table) -> None:
        self.table_columns[table.tablename] = []

    def add_column(self, table: Table, column: Column) -> None:
        labels: list[str] = []
        if column.columnname in table.primary_key:
            labels.append("PK")
        if any(column.columnname in foreign_key.sourcecolumns for foreign_key in table.foreign_keys):
            labels.append("FK")
        label_suffix = f" {', '.join(labels)}" if labels else ""
        self.table_columns[table.tablename].append(
            f"    {_strip_sql_type_size(column.type)} {column.columnname}{label_suffix}"
        )

    def add_primary_key(self, table: Table) -> None:
        return None

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        source_columns = [
            self.table_column_lookup[table.tablename][column_name]
            for column_name in foreign_key.sourcecolumns
        ]
        connector = "}o--o|" if any(column.nullable for column in source_columns) else "}|--o|"
        label = ", ".join(foreign_key.sourcecolumns) + " -> " + ", ".join(foreign_key.targetcolumns)
        self.relationships.append(
            f'  {table.tablename} {connector} {foreign_key.targettable} : "{label}"'
        )

    def end_table(self, table: Table) -> None:
        return None

    def add_datalist(self, datalist: DataList) -> None:
        return None

    def build(self) -> str:
        return "\n".join(self.lines)


class StructureTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.lines: list[str] = []

    def start_schema(self, rel_schema: RelSchema) -> None:
        self.lines = []

    def end_schema(self, rel_schema: RelSchema) -> None:
        return None

    def start_table(self, table: Table) -> None:
        self.lines.append(
            f"- table: {table.tablename}({', '.join(column.columnname for column in table.columns)})"
        )

    def add_column(self, table: Table, column: Column) -> None:
        return None

    def add_primary_key(self, table: Table) -> None:
        return None

    def add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        self.lines.append(
            f"- fk: {table.tablename}({', '.join(foreign_key.sourcecolumns)})->"
            f"{foreign_key.targettable}({', '.join(foreign_key.targetcolumns)})"
        )

    def end_table(self, table: Table) -> None:
        return None

    def add_datalist(self, datalist: DataList) -> None:
        return None

    def build(self) -> str:
        return "\n".join(self.lines)
