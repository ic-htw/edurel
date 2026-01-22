"""SQL to YAML transpiler using sqlglot."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import sqlglot
from sqlglot import exp
import yaml


def sql_to_yaml(
    sql_path: str,
    dialect: str = "postgres",
    yaml_path: Optional[str] = None
) -> str:
    """
    Transpile SQL DDL statements to YAML format.

    Args:
        sql_path: Path to the SQL file
        dialect: SQL dialect (e.g., 'postgres', 'mysql', 'sqlite')
        yaml_path: Optional path to write YAML output. If None, returns YAML string.

    Returns:
        YAML string representation of the database schema

    Example:
        >>> yaml_output = sql_to_yaml('schema.sql', 'postgres', 'schema.yaml')
    """
    # Read SQL file
    sql_path_obj = Path(sql_path)
    if not sql_path_obj.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql_content = sql_path_obj.read_text(encoding='utf-8')

    # Parse SQL statements
    statements = sqlglot.parse(sql_content, dialect=dialect)

    # Extract schema information
    tables = {}
    alter_statements = []

    for statement in statements:
        if statement is None:
            continue

        if isinstance(statement, exp.Create) and statement.kind == "TABLE":
            table_info = _extract_table_info(statement)
            if table_info:
                tables[table_info['name']] = table_info

        elif isinstance(statement, exp.Alter):
            alter_statements.append(statement)

    # Process ALTER TABLE statements for foreign keys
    for alter_stmt in alter_statements:
        _process_alter_table(alter_stmt, tables)

    # Convert to YAML structure
    yaml_data = {
        'tables': list(tables.values())
    }

    # Generate YAML string
    yaml_output = yaml.dump(
        yaml_data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True
    )

    # Write to file if path provided
    if yaml_path:
        yaml_path_obj = Path(yaml_path)
        yaml_path_obj.parent.mkdir(parents=True, exist_ok=True)
        yaml_path_obj.write_text(yaml_output, encoding='utf-8')

    return yaml_output


def _extract_table_info(create_stmt: exp.Create) -> Optional[Dict[str, Any]]:
    """Extract table information from CREATE TABLE statement."""
    table_name = create_stmt.this.this.name


    table_info = {
        'name': table_name,
        'columns': [],
        'primary_key': [],
        'foreign_keys': []
    }

    # Extract column definitions
    if create_stmt.this and hasattr(create_stmt.this, 'expressions'):
        for expr in create_stmt.this.expressions:
            if isinstance(expr, exp.ColumnDef):
                column_info = _extract_column_info(expr)
                if column_info:
                    table_info['columns'].append(column_info)

            elif isinstance(expr, exp.PrimaryKey):
                # Extract primary key columns
                pk_columns = _extract_key_columns(expr)
                table_info['primary_key'].extend(pk_columns)

            elif isinstance(expr, exp.ForeignKey):
                # Extract foreign key constraint
                fk_info = _extract_foreign_key_info(expr)
                if fk_info:
                    table_info['foreign_keys'].append(fk_info)

    # Remove empty primary_key and foreign_keys if not used
    if not table_info['primary_key']:
        del table_info['primary_key']
    if not table_info['foreign_keys']:
        del table_info['foreign_keys']

    return table_info


def _extract_column_info(column_def: exp.ColumnDef) -> Optional[Dict[str, Any]]:
    """Extract column information from column definition."""
    column_name = column_def.this.name

    column_info = {
        'name': column_name,
        'type': None,
        'constraints': None
    }

    # Extract data type
    if column_def.kind:
        column_info['type'] = column_def.kind.sql().upper()

    # Extract constraints
    constraints = []
    for constraint in column_def.constraints:
        ckind  = constraint.kind 
        if isinstance(ckind, exp.NotNullColumnConstraint):
            constraints.append("NOT NULL")
        elif isinstance(ckind, exp.UniqueColumnConstraint):
            constraints.append("UNIQUE")
        elif isinstance(ckind, exp.PrimaryKeyColumnConstraint):
            constraints.append("PRIMARY KEY")
        elif isinstance(ckind, exp.DefaultColumnConstraint):
            default_value = constraint.this.sql() if constraint.this else ""
            constraints.append(f"DEFAULT {default_value}")
        elif isinstance(ckind, exp.AutoIncrementColumnConstraint):
            constraints.append("AUTO_INCREMENT")

    if constraints:
        column_info['constraints'] = " ".join(constraints)
    else:
        # Remove constraints field if empty
        del column_info['constraints']

    return column_info


def _extract_key_columns(key_expr: exp.PrimaryKey) -> List[str]:
    """Extract column names from primary key or foreign key expression."""
    columns = []
    if hasattr(key_expr, 'expressions'):
        for expr in key_expr.expressions:
            if isinstance(expr.this, exp.Column):
                columns.append(expr.name)
    return columns


def _extract_foreign_key_info(fk_expr: exp.ForeignKey) -> Optional[Dict[str, Any]]:
    """Extract foreign key constraint information."""
    fk_info = {
        'columns': [],
        'ref_table': None,
        'ref_columns': []
    }

    # Extract FK columns
    if hasattr(fk_expr, 'expressions'):
        for expr in fk_expr.expressions:
            if isinstance(expr, exp.Identifier):
                fk_info['columns'].append(expr.name)

    # Extract referenced table and columns
    # Access reference through args dictionary
    ref = fk_expr.args.get('reference')
    if ref:
        if hasattr(ref, 'this') and ref.this.this:
            fk_info['ref_table'] = ref.this.this.name

        if hasattr(ref, 'expressions'):
            for expr in ref.this.expressions:
                if isinstance(expr, exp.Identifier):
                    fk_info['ref_columns'].append(expr.name)

    # Add constraint name if available
    # if hasattr(fk_expr, 'name') and fk_expr.name:
    #     fk_info['name'] = fk_expr.name

    # Generate default name if not provided
    # if 'name' not in fk_info and fk_info['columns'] and fk_info['ref_table']:
    #     col_name = fk_info['columns'][0]
    #     fk_info['name'] = f"fk_{fk_info['ref_table']}_{col_name}"

    return fk_info if fk_info['ref_table'] else None


def _process_alter_table(alter_stmt: exp.Alter, tables: Dict[str, Dict[str, Any]]):
    """Process ALTER TABLE statement to extract foreign key constraints."""
    table_name = alter_stmt.this.name

    # Ensure table exists
    if table_name not in tables:
        return

    # Ensure foreign_keys list exists
    if 'foreign_keys' not in tables[table_name]:
        tables[table_name]['foreign_keys'] = []

    # Extract ADD CONSTRAINT for foreign keys
    for action in alter_stmt.actions:
        if isinstance(action, exp.AddConstraint):
            for constraint in action.expressions:
                constraint_name = constraint.name
                fk_constraint = constraint.expressions[0]
                if isinstance(fk_constraint, exp.ForeignKey):
                    fk_info = _extract_foreign_key_info(fk_constraint)
                    if fk_info:
                        tables[table_name]['foreign_keys'].append(fk_info)
    # Remove empty foreign_keys if not used
    if not tables[table_name]['foreign_keys']:
        del tables[table_name]['foreign_keys']
