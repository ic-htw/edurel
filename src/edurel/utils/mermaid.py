import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
import ipywidgets as widgets
from IPython.display import display, HTML


def schema_to_mermaid(schema: Dict[str, Any]) -> str:
    """
    Convert schema dictionary to Mermaid ER diagram syntax.
    Args:
        schema: Schema dictionary loaded from YAML
    Returns:
        Mermaid diagram code as string
    """
    lines = ["erDiagram"]
    tables = schema.get('tables', [])

    # Generate table definitions
    for table in tables:
        table_name = table['name']
        columns = table.get('columns', [])
        pk_cols = set(table.get('primary_key', []))
        lines.append(f"    {table_name} {{")
        for col in columns:
            col_name = col['col']
            col_type = col['type']
            nullable = col.get('nullable', True)
            # Add PK or NULL constraint markers
            constraint = ""
            if col_name in pk_cols:
                constraint = " PK"
            # elif not nullable:
            #     constraint = " NOT_NULL"
            lines.append(f"        {col_type} {col_name}{constraint}")
        lines.append("    }")

    # Generate relationships from foreign keys
    for table in tables:
        table_name = table['name']
        foreign_keys = table.get('foreign_keys', [])
        for fk in foreign_keys:
            ref_table = fk['ref_table']
            fk_cols = ', '.join(fk['columns'])
            ref_cols = ', '.join(fk['ref_columns'])
            # Mermaid relationship: many-to-one (orders to users)
            # Format: SOURCE }o--|| TARGET : "relationship"
            lines.append(f'    {table_name} }}o--|| {ref_table} : "{fk_cols} -> {ref_cols}"')
    return "\n".join(lines)

