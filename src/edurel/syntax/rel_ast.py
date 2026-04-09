from dataclasses import dataclass, field

@dataclass
class Column:
    """Represents a column with name, type, and nullable flag."""

    columnname: str
    type: str
    nullable: bool = False

    def __str__(self) -> str:
        nullable_str = " (null)" if self.nullable else " (not null)"
        return f"{self.columnname}: {self.type}{nullable_str}"


@dataclass
class ForeignKey:
    """Represents a foreign key constraint."""

    fkname: str | None = None
    sourcecolumns: list[str] = field(default_factory=list)
    targettable: str = ""
    targetcolumns: list[str] = field(default_factory=list)
    is_cycle: bool = False

    def __str__(self) -> str:
        src_cols = ", ".join(self.sourcecolumns)
        tgt_cols = ", ".join(self.targetcolumns)
        fkname_str = f"{self.fkname}: " if self.fkname else ""
        cycle_str = " [cycle]" if self.is_cycle else ""
        return f"{fkname_str}({src_cols}) -> {self.targettable}({tgt_cols}){cycle_str}"


@dataclass
class DataList:
    """Represents predefined data for a table."""

    tablename: str
    values: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        values_str = ", ".join(self.values)
        return f"DataList: {self.tablename}\n  Values: {values_str}"


@dataclass
class Table:
    """Represents a table with columns, primary key, and foreign keys."""

    tablename: str
    columns: list[Column] = field(default_factory=list)
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    level: int = 0

    def __str__(self) -> str:
        cols_str = "\n    ".join(str(col) for col in self.columns)
        pk_str = ", ".join(self.primary_key)
        result = f"Table: {self.tablename}\n"
        if self.level != 0:
            result += f"  Level: {self.level}\n"
        result += f"  Primary Key: [{pk_str}]\n  Columns:\n    {cols_str}"

        if self.foreign_keys:
            fks_str = "\n    ".join(str(fk) for fk in self.foreign_keys)
            result += f"\n  Foreign Keys:\n    {fks_str}"

        return result


@dataclass
class RelSchema:
    """Complete relational schema AST."""

    tables: list[Table] = field(default_factory=list)
    datalists: list[DataList] = field(default_factory=list)

    def __str__(self) -> str:
        sections = []
        if self.tables:
            tables_str = "\n\n".join(str(t) for t in self.tables)
            sections.append(f"=== TABLES ===\n{tables_str}")
        if self.datalists:
            datalists_str = "\n\n".join(str(d) for d in self.datalists)
            sections.append(f"=== DATALISTS ===\n{datalists_str}")
        return "\n\n".join(sections) if sections else "No tables"


class RelAstFactory:
    """Builds the relational schema AST from parsed YAML data."""

    @classmethod
    def create_schema(cls, data: dict) -> RelSchema:
        return RelSchema(
            tables=[cls.create_table(table) for table in data.get("tables", [])],
            datalists=[
                cls.create_datalist(datalist) for datalist in data.get("datalists", [])
            ],
        )

    @staticmethod
    def create_column(data: dict) -> Column:
        return Column(
            columnname=data["columnname"],
            type=data["type"],
            nullable=data.get("nullable", False),
        )

    @classmethod
    def create_foreign_key(cls, data: dict) -> ForeignKey:
        return ForeignKey(
            fkname=data.get("fkname"),
            sourcecolumns=list(data["sourcecolumns"]),
            targettable=data["targettable"],
            targetcolumns=list(data["targetcolumns"]),
        )

    @classmethod
    def create_datalist(cls, data: dict) -> DataList:
        return DataList(
            tablename=data["tablename"],
            values=list(data["values"]),
        )

    @classmethod
    def create_table(cls, data: dict) -> Table:
        return Table(
            tablename=data["tablename"],
            columns=[cls.create_column(column) for column in data["columns"]],
            primary_key=list(data.get("primary_key", [])),
            foreign_keys=[
                cls.create_foreign_key(foreign_key)
                for foreign_key in data.get("foreign_keys", [])
            ],
        )


def enrich_ast(rel_schema: RelSchema) -> None:
    tables_by_name = {table.tablename: table for table in rel_schema.tables}

    for table in rel_schema.tables:
        table.level = 0
        for foreign_key in table.foreign_keys:
            foreign_key.is_cycle = False

    visit_state: dict[str, str] = {}

    def mark_cycles(table: Table) -> None:
        visit_state[table.tablename] = "visiting"
        for foreign_key in table.foreign_keys:
            target_table = tables_by_name.get(foreign_key.targettable)
            if target_table is None:
                continue
            target_state = visit_state.get(target_table.tablename)
            if target_state == "visiting":
                foreign_key.is_cycle = True
                continue
            if target_state == "visited":
                continue
            mark_cycles(target_table)
        visit_state[table.tablename] = "visited"

    for table in rel_schema.tables:
        if visit_state.get(table.tablename) is None:
            mark_cycles(table)

    dependency_count: dict[str, int] = {table.tablename: 0 for table in rel_schema.tables}
    dependents_by_table: dict[str, list[Table]] = {
        table.tablename: [] for table in rel_schema.tables
    }

    for table in rel_schema.tables:
        seen_targets: set[str] = set()
        for foreign_key in table.foreign_keys:
            if foreign_key.is_cycle:
                continue
            target_table = tables_by_name.get(foreign_key.targettable)
            if target_table is None or target_table.tablename in seen_targets:
                continue
            seen_targets.add(target_table.tablename)
            dependency_count[table.tablename] += 1
            dependents_by_table[target_table.tablename].append(table)

    ready = [table for table in rel_schema.tables if dependency_count[table.tablename] == 0]
    for table in ready:
        table.level = 1

    index = 0
    while index < len(ready):
        table = ready[index]
        index += 1
        for dependent in dependents_by_table[table.tablename]:
            dependent.level = max(dependent.level, table.level + 1)
            dependency_count[dependent.tablename] -= 1
            if dependency_count[dependent.tablename] == 0:
                if dependent.level == 0:
                    dependent.level = 1
                ready.append(dependent)

    for table in rel_schema.tables:
        if table.level == 0:
            table.level = 1

def validate_ast(rel_schema: RelSchema) -> None:
    errors: list[str] = []

    table_names = [table.tablename for table in rel_schema.tables]
    seen_table_names: set[str] = set()
    duplicate_table_names = {
        table_name for table_name in table_names if table_name in seen_table_names or seen_table_names.add(table_name)
    }
    for table_name in sorted(duplicate_table_names):
        errors.append(f"Duplicate table name '{table_name}'.")

    tables_by_name = {}
    for table in rel_schema.tables:
        if table.tablename not in tables_by_name:
            tables_by_name[table.tablename] = table

    for table in rel_schema.tables:
        column_names = [column.columnname for column in table.columns]
        seen_column_names: set[str] = set()
        duplicate_column_names = {
            column_name
            for column_name in column_names
            if column_name in seen_column_names or seen_column_names.add(column_name)
        }
        for column_name in sorted(duplicate_column_names):
            errors.append(
                f"Table '{table.tablename}' has duplicate column name '{column_name}'."
            )

        column_name_set = set(column_names)
        for primary_key in table.primary_key:
            if primary_key not in column_name_set:
                errors.append(
                    f"Table '{table.tablename}' primary key '{primary_key}' is not a column."
                )

        named_foreign_keys = [foreign_key.fkname for foreign_key in table.foreign_keys if foreign_key.fkname]
        seen_fk_names: set[str] = set()
        duplicate_fk_names = {
            fk_name for fk_name in named_foreign_keys if fk_name in seen_fk_names or seen_fk_names.add(fk_name)
        }
        for fk_name in sorted(duplicate_fk_names):
            errors.append(
                f"Table '{table.tablename}' has duplicate foreign key name '{fk_name}'."
            )

        for foreign_key in table.foreign_keys:
            for source_column in foreign_key.sourcecolumns:
                if source_column not in column_name_set:
                    errors.append(
                        f"Foreign key '{foreign_key.fkname or '<unnamed>'}' in table "
                        f"'{table.tablename}' references missing source column '{source_column}'."
                    )

            target_table = tables_by_name.get(foreign_key.targettable)
            if target_table is None:
                errors.append(
                    f"Foreign key '{foreign_key.fkname or '<unnamed>'}' in table "
                    f"'{table.tablename}' references missing target table "
                    f"'{foreign_key.targettable}'."
                )
                continue

            target_primary_keys = set(target_table.primary_key)
            for target_column in foreign_key.targetcolumns:
                if target_column not in target_primary_keys:
                    errors.append(
                        f"Foreign key '{foreign_key.fkname or '<unnamed>'}' in table "
                        f"'{table.tablename}' references target column '{target_column}' "
                        f"that is not in primary key of table '{target_table.tablename}'."
                    )

    datalist_names = [datalist.tablename for datalist in rel_schema.datalists]
    seen_datalist_names: set[str] = set()
    duplicate_datalist_names = {
        datalist_name
        for datalist_name in datalist_names
        if datalist_name in seen_datalist_names or seen_datalist_names.add(datalist_name)
    }
    for datalist_name in sorted(duplicate_datalist_names):
        errors.append(f"Duplicate datalist table name '{datalist_name}'.")

    for datalist in rel_schema.datalists:
        if datalist.tablename not in tables_by_name:
            errors.append(
                f"Datalist references missing table '{datalist.tablename}'."
            )

    if errors:
        joined_errors = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"AST validation failed:\n{joined_errors}")
