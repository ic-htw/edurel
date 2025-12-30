import re
import yaml

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

