import re
from pathlib import Path
from typing import Optional, Callable, List, Any
from .duckdb import Db


def md_sql(str):
    return f"```sql\n{str}\n```"

def md_yaml(str):
    return f"```yaml\n{str}\n```"

def md_plain(str):
    return f"```plaintext\n{str}\n```"


def sql_extract(text):
    """Extract SQL code from text (supports both plain text and markdown).

    Args:
        text: A string with embedded SQL statement(s)

    Returns:
        str: Extracted SQL code, or empty string if no SQL found
    """
    # First, try to extract from markdown code blocks
    # Look for ```sql ... ``` blocks
    sql_block_pattern = r'```sql\s*\n(.*?)\n```'
    matches = re.findall(sql_block_pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Look for generic ``` ... ``` blocks that might contain SQL
    generic_block_pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(generic_block_pattern, text, re.DOTALL)
    for match in matches:
        # Check if it looks like SQL (starts with common SQL keywords)
        if re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b',
                   match, re.IGNORECASE):
            return match.strip()

    # If no markdown blocks, try to extract SQL from plain text
    # Look for SQL statements (starting with common keywords at line start)
    sql_pattern = r'(?:^|\n)\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b.*?)(?=\n\n|\Z)'
    matches = re.findall(sql_pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if matches:
        return matches[0].strip()

    return ""


def csv_to_parquet(
    in_path: str,
    fn: str,
    spec: str,
    verbose: bool = False,
    out_path: Optional[str] = None
) -> None:
    """
    Read CSV files from a directory and export them as Parquet files.

    Args:
        in_path: Path to directory containing CSV files
        fn: Either "*" to process all CSV files, or a list of table names
        spec: DuckDB CSV reading options (e.g., "header=true, delimiter=','")
        verbose: If True, prints sample data from each table
        out_path: Path to directory where Parquet files will be written

    Raises:
        ValueError: If in_path is not provided, not a directory, no files found,
                    or out_path is not provided

    Example:
        >>> csv_to_parquet(
        ...     in_path="./data/csv",
        ...     fn="*",
        ...     spec="header=true",
        ...     out_path="./data/parquet",
        ...     verbose=True
        ... )
    """
    if in_path is None:
        raise ValueError("in_path must be provided")
    p = Path(in_path)
    if not p.is_dir():
        raise ValueError(f"in_path {in_path} is not a directory")

    if fn == "*":
        files = sorted([f.name for f in p.iterdir() if f.is_file()])
        tns = [Path(f).stem for f in files]
    else:
        tns = list(fn)
    if len(tns) == 0:
        raise ValueError(f"No files found in {in_path} with fn={fn}")

    if out_path is None:
        raise ValueError("out_path must be provided to export parquet files")

    db = Db.mem()
    for tn in tns:
        f = p / f"{tn}.csv"
        sql_read = f"""
        create or replace table {tn} as
        select * from read_csv('{str(f)}', {spec});
        """
        db.exe(sql_read)

        if verbose:
            print(f"Table: {tn}")
            db.print(f"select * from {tn} limit 2;")

        out_f = Path(out_path) / f"{tn}.parquet"
        db.exe(f"COPY (SELECT * FROM {tn}) TO '{str(out_f)}' (FORMAT 'parquet');")


def gslice(spec: str) -> Callable[[List[Any]], List[Any]]:
    """Create a generalized slicing function from a spec string.

    Args:
        spec: String of form "i1, i2:i3, i4, i5:i6" where indices are integers.
              Individual indices (i1, i4) select single elements.
              Range slices (i2:i3, i5:i6) select ranges [start:end) like Python slicing.
              Negative indices are supported.
              Empty start/end in ranges use list boundaries (e.g., ":3" or "5:").

    Returns:
        Function that takes a list and returns elements matching the spec.

    Examples:
        >>> f = gslice("0, 2:5, 7")
        >>> f(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        ['a', 'c', 'd', 'e', 'h']

        >>> g = gslice("1:3, -1")
        >>> g([10, 20, 30, 40, 50])
        [20, 30, 50]

        >>> h = gslice(":2, -2:")
        >>> h(['x', 'y', 'z', 'w'])
        ['x', 'y', 'z', 'w']
    """
    # Parse the spec string
    parts = [p.strip() for p in spec.split(',')]

    def slicer(lst: List[Any]) -> List[Any]:
        result = []
        for part in parts:
            if ':' in part:
                # Range slice
                slice_parts = part.split(':', 1)
                start_str = slice_parts[0].strip()
                end_str = slice_parts[1].strip()

                start = int(start_str) if start_str else None
                end = int(end_str) if end_str else None

                result.extend(lst[start:end])
            else:
                # Individual index
                idx = int(part)
                result.append(lst[idx])
        return result

    return slicer


def ml_unindent(text: str) -> str:
    """Remove indentation from a multiline string based on first non-empty line.

    Shifts the entire multiline string to the left by removing the indentation
    of the first non-empty line from all lines.

    Args:
        text: Multiline string to unindent

    Returns:
        str: Unindented string with consistent left alignment

    Examples:
        >>> text = '''
        ...     def hello():
        ...         print("world")
        ... '''
        >>> print(ml_unindent(text))
        <BLANKLINE>
        def hello():
            print("world")
        <BLANKLINE>

        >>> text = '    Line 1\\n        Line 2\\n    Line 3'
        >>> print(ml_unindent(text))
        Line 1
            Line 2
        Line 3
    """
    if not text:
        return text

    lines = text.split('\n')

    # Find the first non-empty line
    first_indent = None
    for line in lines:
        if line.strip():
            # Count leading whitespace
            first_indent = len(line) - len(line.lstrip())
            break

    # If all lines are empty, return original
    if first_indent is None:
        return text

    # Remove the indent from all lines
    result_lines = []
    for line in lines:
        if line.strip():
            # Remove up to first_indent spaces from non-empty lines
            if len(line) >= first_indent and line[:first_indent].strip() == '':
                result_lines.append(line[first_indent:])
            else:
                # Line has less indent than expected, keep as is
                result_lines.append(line.lstrip())
        else:
            # Keep empty lines as empty
            result_lines.append(line)

    return '\n'.join(result_lines)


def er_to_mermaid(schema: dict) -> str:
    """Convert ER diagram from YAML format to Mermaid ER diagram syntax.

    Args:
        schema: Dictionary containing ER diagram specification with keys:
                - entities: List of entity definitions
                - associative_entities: List of associative entity definitions
                - relationships: List of relationship definitions
                - inheritances: List of inheritance hierarchies
                - valuelists: List of valuelist definitions

    Returns:
        str: Mermaid ER diagram code

    Example:
        >>> schema = {
        ...     'entities': [
        ...         {'entityname': 'Student', 'key': 'StudentID',
        ...          'attributes': [{'attributename': 'Name', 'type': 'TEXT'}]}
        ...     ],
        ...     'relationships': [
        ...         {'relationshipname': 'Enrolls',
        ...          'entities': [
        ...              {'entityname': 'Student', 'role': 'student'},
        ...              {'entityname': 'Course', 'role': 'course'}
        ...          ],
        ...          'cardinality': {'student': 'MANY', 'course': 'MANY'}}
        ...     ]
        ... }
        >>> print(er_to_mermaid(schema))
        erDiagram
            Student {
                TEXT StudentID PK
                TEXT Name
            }
        ...
    """
    lines = ["erDiagram"]

    # Helper function to map cardinality to Mermaid notation
    def cardinality_to_mermaid(card: str) -> str:
        """Convert cardinality notation to Mermaid symbols.

        Args:
            card: ONE, MANY, OPTIONAL_ONE, or OPTIONAL_MANY

        Returns:
            str: Mermaid cardinality symbol (||, |o, }|, }o)
        """
        mapping = {
            'ONE': '||',
            'MANY': '}|',
            'OPTIONAL_ONE': '|o',
            'OPTIONAL_MANY': '}o'
        }
        return mapping.get(card, '||')

    # Process regular entities
    entities = schema.get('entities', [])
    for entity in entities:
        entity_name = entity['entityname']
        key = entity.get('key')
        attributes = entity.get('attributes', [])

        lines.append(f"    {entity_name} {{")

        # Add key as PK
        if key:
            lines.append(f"        string {key} PK")

        # Add attributes
        for attr in attributes:
            attr_name = attr['attributename']
            attr_type = attr['type']
            lines.append(f"        {attr_type} {attr_name}")

        lines.append("    }")

    # Process valuelists (they become entities)
    valuelists = schema.get('valuelists', [])
    for vl in valuelists:
        vl_name = vl['valuelistname']
        lines.append(f"    {vl_name} {{")
        lines.append("        INTEGER ID PK")
        lines.append("        TEXT Description")
        lines.append("        BOOLEAN IsValid")
        lines.append("        INTEGER SortOrder")
        lines.append("    }")

    # Process associative entities
    associative_entities = schema.get('associative_entities', [])
    for ae in associative_entities:
        ae_name = ae['associationname']
        key = ae.get('key')
        attributes = ae.get('attributes', [])

        lines.append(f"    {ae_name} {{")

        # Add key as PK if present
        if key:
            lines.append(f"        string {key} PK")

        # Add attributes
        for attr in attributes:
            attr_name = attr['attributename']
            attr_type = attr['type']
            lines.append(f"        {attr_type} {attr_name}")

        lines.append("    }")

    # Process relationships from associative entities
    for ae in associative_entities:
        ae_name = ae['associationname']

        # Process associations
        associations = ae.get('associations', [])
        for assoc in associations:
            target = assoc['targetentity']
            role = assoc.get('role', target)
            card = assoc.get('cardinality', 'ONE')

            # Associative entity to target entity
            card_symbol = cardinality_to_mermaid(card)
            lines.append(f"    {ae_name} }}o--{card_symbol} {target} : \"{role}\"")

        # Process identified_by relationships
        identified_by = ae.get('identified_by', [])
        for ident in identified_by:
            target = ident['targetentity']
            card = ident.get('cardinality', 'ONE')
            card_symbol = cardinality_to_mermaid(card)
            lines.append(f"    {ae_name} }}|--{card_symbol} {target} : \"identified by\"")

    # Process regular relationships
    relationships = schema.get('relationships', [])
    for rel in relationships:
        rel_name = rel['relationshipname']
        entities_list = rel.get('entities', [])
        cardinality = rel.get('cardinality', {})

        if len(entities_list) == 2:
            entity1 = entities_list[0]
            entity2 = entities_list[1]

            entity1_name = entity1['entityname']
            entity2_name = entity2['entityname']

            role1 = entity1.get('role', entity1_name)
            role2 = entity2.get('role', entity2_name)

            # Get cardinalities (default to ONE if not specified)
            card1 = cardinality.get(role1, 'ONE')
            card2 = cardinality.get(role2, 'ONE')

            # Build relationship line
            card1_symbol = cardinality_to_mermaid(card1)
            card2_symbol = cardinality_to_mermaid(card2)

            lines.append(f"    {entity1_name} {card1_symbol}--{card2_symbol} {entity2_name} : \"{rel_name}\"")

    # Process inheritances
    inheritances = schema.get('inheritances', [])
    for inh in inheritances:
        super_entity = inh['superentity']
        sub_entities = inh.get('subentities', [])

        for sub in sub_entities:
            # Represent inheritance as a relationship
            lines.append(f"    {sub} ||--|| {super_entity} : \"inherits from\"")

    return "\n".join(lines)
