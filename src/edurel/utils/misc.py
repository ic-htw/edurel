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
