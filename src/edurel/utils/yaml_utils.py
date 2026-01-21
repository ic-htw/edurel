import re
import yaml
from fnmatch import fnmatch
from typing import Any, Dict


def yaml_to_yaml(yaml_input: str, spec: str) -> str:
    """Transform YAML schema input according to specification.

    Args:
        yaml_input: YAML string containing relational database schema
        spec: Multi-line specification string with transformation steps

    Returns:
        Transformed YAML string

    Spec language:
        del table pattern:<pattern>              - Delete tables matching pattern
        del table index:<index_spec>             - Delete tables by index
        del column <table> pattern:<pattern>     - Delete columns in table matching pattern
        del column <table> index:<index_spec>    - Delete columns in table by index
        del column * pattern:<pattern>           - Delete columns matching pattern in all tables
        del fk pattern:<pattern>                 - Delete foreign keys matching pattern
        del fk index:<index_spec>                - Delete foreign keys by index

    Index spec formats:
        0           - Single index
        [0,2,4]     - List of indexes
        [1:5]       - Slice
        [::2]       - Slice with step
        [1:3,5:7]   - Multiple slices/indexes
    """
    # Parse YAML
    schema = yaml.safe_load(yaml_input)

    # Process each line of spec
    for line in spec.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        schema = _apply_transformation(schema, line)

    # Convert back to YAML
    return yaml.dump(schema, default_flow_style=False, sort_keys=False)


def _apply_transformation(schema: Dict[str, Any], spec_line: str) -> Dict[str, Any]:
    """Apply a single transformation step to schema."""

    # Parse the spec line
    match = re.match(r'del\s+table\s+pattern:(.+)', spec_line)
    if match:
        pattern = match.group(1).strip()
        return _delete_tables_by_pattern(schema, pattern)

    match = re.match(r'del\s+table\s+index:(.+)', spec_line)
    if match:
        index_spec = match.group(1).strip()
        return _delete_tables_by_index(schema, index_spec)

    match = re.match(r'del\s+column\s+(\S+)\s+pattern:(.+)', spec_line)
    if match:
        table = match.group(1).strip()
        pattern = match.group(2).strip()
        if table == '*':
            return _delete_columns_all_tables_by_pattern(schema, pattern)
        else:
            return _delete_columns_by_pattern(schema, table, pattern)

    match = re.match(r'del\s+column\s+(\S+)\s+index:(.+)', spec_line)
    if match:
        table = match.group(1).strip()
        index_spec = match.group(2).strip()
        return _delete_columns_by_index(schema, table, index_spec)

    match = re.match(r'del\s+fk\s+pattern:(.+)', spec_line)
    if match:
        pattern = match.group(1).strip()
        return _delete_fks_by_pattern(schema, pattern)

    match = re.match(r'del\s+fk\s+index:(.+)', spec_line)
    if match:
        index_spec = match.group(1).strip()
        return _delete_fks_by_index(schema, index_spec)

    raise ValueError(f"Invalid spec line: {spec_line}")


def _delete_tables_by_pattern(schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Delete tables matching pattern."""
    if 'tables' not in schema:
        return schema

    schema['tables'] = [
        table for table in schema['tables']
        if not fnmatch(table.get('tablename', ''), pattern)
    ]
    return schema


def _delete_tables_by_index(schema: Dict[str, Any], index_spec: str) -> Dict[str, Any]:
    """Delete tables by index specification."""
    if 'tables' not in schema:
        return schema

    indexes = _parse_index_spec(index_spec, len(schema['tables']))
    schema['tables'] = [
        table for i, table in enumerate(schema['tables'])
        if i not in indexes
    ]
    return schema


def _delete_columns_by_pattern(schema: Dict[str, Any], tablename: str, pattern: str) -> Dict[str, Any]:
    """Delete columns matching pattern in specific table."""
    if 'tables' not in schema:
        return schema

    for table in schema['tables']:
        if table.get('tablename') == tablename and 'columns' in table:
            table['columns'] = [
                col for col in table['columns']
                if not fnmatch(col.get('columnname', ''), pattern)
            ]
    return schema


def _delete_columns_by_index(schema: Dict[str, Any], tablename: str, index_spec: str) -> Dict[str, Any]:
    """Delete columns by index in specific table."""
    if 'tables' not in schema:
        return schema

    for table in schema['tables']:
        if table.get('tablename') == tablename and 'columns' in table:
            indexes = _parse_index_spec(index_spec, len(table['columns']))
            table['columns'] = [
                col for i, col in enumerate(table['columns'])
                if i not in indexes
            ]
    return schema


def _delete_columns_all_tables_by_pattern(schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Delete columns matching pattern across all tables."""
    if 'tables' not in schema:
        return schema

    for table in schema['tables']:
        if 'columns' in table:
            table['columns'] = [
                col for col in table['columns']
                if not fnmatch(col.get('columnname', ''), pattern)
            ]
    return schema


def _delete_fks_by_pattern(schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Delete foreign keys matching pattern."""
    if 'tables' not in schema:
        return schema

    for table in schema['tables']:
        if 'foreign_keys' in table:
            table['foreign_keys'] = [
                fk for fk in table['foreign_keys']
                if not fnmatch(fk.get('fkname', ''), pattern)
            ]
    return schema


def _delete_fks_by_index(schema: Dict[str, Any], index_spec: str) -> Dict[str, Any]:
    """Delete foreign keys by index across all tables."""
    if 'tables' not in schema:
        return schema

    for table in schema['tables']:
        if 'foreign_keys' in table:
            indexes = _parse_index_spec(index_spec, len(table['foreign_keys']))
            table['foreign_keys'] = [
                fk for i, fk in enumerate(table['foreign_keys'])
                if i not in indexes
            ]
    return schema


def _parse_index_spec(spec: str, length: int) -> set:
    """Parse index specification into set of indexes.

    Supports:
        0           - Single index
        [0,2,4]     - List of indexes
        [1:5]       - Slice
        [::2]       - Slice with step
        [1:3,5:7]   - Multiple slices/indexes
    """
    indexes = set()

    # Single index (no brackets)
    if not spec.startswith('['):
        indexes.add(int(spec))
        return indexes

    # Remove brackets
    spec = spec[1:-1]

    # Split by comma
    parts = spec.split(',')

    for part in parts:
        part = part.strip()

        # Slice notation
        if ':' in part:
            # Parse slice
            slice_parts = part.split(':')
            start = int(slice_parts[0]) if slice_parts[0] else None
            stop = int(slice_parts[1]) if len(slice_parts) > 1 and slice_parts[1] else None
            step = int(slice_parts[2]) if len(slice_parts) > 2 and slice_parts[2] else None

            # Convert slice to indexes
            slice_obj = slice(start, stop, step)
            indexes.update(range(*slice_obj.indices(length)))
        else:
            # Single index
            indexes.add(int(part))

    return indexes


def yaml_print(data):
    """
    Print a YAML dictionary structure in a human-readable format.

    Args:
        data: Dictionary corresponding to the parsed YAML file

    Returns:
        None
    """

    print(yaml.dump(data, default_flow_style=False, sort_keys=False))

def yaml_remove_tags(data, omit_tags):
    """
    Remove specified tags (keys) from a YAML dictionary structure.

    Recursively traverses the data structure and removes any keys that match
    the tags in the omit_tags list.

    Args:
        data: Dictionary corresponding to the parsed YAML file
        omit_tags: List of tag names (keys) to omit from the result

    Returns:
        Dictionary with specified tags removed

    Example:
        >>> data = {"name": "test", "id": 1, "meta": {"id": 2, "value": "x"}}
        >>> yaml_remove_tags(data, ["id"])
        {"name": "test", "meta": {"value": "x"}}
    """
    if isinstance(data, dict):
        return {
            key: yaml_remove_tags(value, omit_tags)
            for key, value in data.items()
            if key not in omit_tags
        }
    elif isinstance(data, list):
        return [yaml_remove_tags(item, omit_tags) for item in data]
    else:
        return data


def yaml_to_mermaid(data, direction="TB"):
    """
    Convert a YAML schema dictionary to Mermaid ER diagram code.

    Args:
        data: Dictionary corresponding to the YAML schema file

    Returns:
        String containing Mermaid ER diagram code

    Example:
        >>> schema = {"tables": [{"tablename": "users", "columns": [...]}]}
        >>> mermaid_code = yaml_to_mermaid(schema)
    """
    lines = ["erDiagram"]
    lines.append(f"    direction {direction}")
    tables = data.get("tables", [])

    # Generate table definitions
    for table in tables:
        tablename = table["tablename"]
        columns = table.get("columns", [])
        pk_cols = set(table.get("primary_key", []))

        lines.append(f"    {tablename} {{")
        for col in columns:
            columnname = col["columnname"]
            col_type = col["type"]
            # Remove size indicators like (9,2) or (255)
            col_type = re.sub(r"\([^)]*\)", "", col_type)

            # Add PK marker if column is in primary key
            constraint = " PK" if columnname in pk_cols else ""
            lines.append(f"        {col_type} {columnname}{constraint}")
        lines.append("    }")

    # Generate relationships from foreign keys
    for table in tables:
        tablename = table["tablename"]
        foreign_keys = table.get("foreign_keys", [])
        for fk in foreign_keys:
            targettable = fk["targettable"]
            sourcecolumns = ", ".join(fk["sourcecolumns"])
            targetcolumns = ", ".join(fk["targetcolumns"])
            # Mermaid relationship: many-to-one
            lines.append(
                f'    {tablename} }}o--|| {targettable} : "{sourcecolumns} -> {targetcolumns}"'
            )

    return "\n".join(lines)

