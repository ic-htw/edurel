import duckdb
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import yaml
import pandas as pd

# ---------------------------------------------------------------------------------------------
# SQL Query Constants
# ---------------------------------------------------------------------------------------------
_SQL_PRIMARY_KEYS = """
    SELECT
      table_name,
      list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names
    FROM duckdb_constraints()
    WHERE constraint_type = 'PRIMARY KEY'
    GROUP BY table_name, constraint_column_names
    ORDER BY table_name;
"""

_SQL_FOREIGN_KEYS = """
    SELECT
      table_name as table_name_src,
      list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names_src,
      referenced_table as table_name_trg,
      list_aggregate(referenced_column_names, 'string_agg', ', ') as col_names_trg
    FROM duckdb_constraints()
    WHERE constraint_type = 'FOREIGN KEY';
"""

# ---------------------------------------------------------------------------------------------
# Query utils
# ---------------------------------------------------------------------------------------------
def sql_print(con: duckdb.DuckDBPyConnection, sql: str) -> None:
    """
    Execute SQL query and print the result.

    Args:
        con: DuckDB connection
        sql: SQL query string to execute
    """
    print(con.sql(sql))


def sql_df(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """
    Execute SQL query and return result as a pandas DataFrame.

    Args:
        con: DuckDB connection
        sql: SQL query string to execute

    Returns:
        pandas DataFrame containing query results
    """
    return con.sql(sql).df()

# ---------------------------------------------------------------------------------------------
# Connection utils
# ---------------------------------------------------------------------------------------------
def mem_con(db_path: Optional[str] = None, verbose: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Create an in-memory DuckDB connection, optionally loading schema and data from a directory.

    The function looks for two SQL files in the db_path directory:
    - schema.sql: DDL statements to create tables and constraints
    - post.sql: DML statements to insert data or perform post-processing

    Args:
        db_path: Path to directory containing schema.sql and/or post.sql files.
                 If None, creates an empty in-memory database.
        verbose: If True, prints status messages about file loading

    Returns:
        DuckDB connection to in-memory database

    Example:
        >>> con = mem_con("./data/my_database", verbose=True)
        >>> con.execute("SELECT * FROM users").fetchall()
    """
    con = duckdb.connect(database=':memory:', read_only=False)
    if db_path is None:
        if verbose:
            print("No db_path. Creating empty in-memory database.")
        return con

    schema_path = Path(db_path) / "schema.sql"
    if schema_path.exists():
        with schema_path.open("r", encoding="utf-8") as f:
            con.execute(f.read())
    else:
        if verbose:
            print("No schema.sql. Creating empty in-memory database.")

    post_path = Path(db_path) / "post.sql"
    if post_path.exists():
        with post_path.open("r", encoding="utf-8") as f:
            con.execute(f.read())
    else:
        if verbose:
            print("No post.sql. Skipping post-processing.")
    return con

def file_con(db_path: str, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """
    Connect to a persistent DuckDB database file.

    Args:
        db_path: Path to directory containing db.duckdb file
        read_only: If True, opens database in read-only mode

    Returns:
        DuckDB connection to the database file

    Raises:
        ValueError: If db.duckdb file does not exist in db_path

    Example:
        >>> con = file_con("./data/my_database", read_only=True)
        >>> con.execute("SELECT * FROM users").fetchall()
    """
    db_file_path = Path(db_path) / "db.duckdb"
    if not db_file_path.exists():
        raise ValueError("No db.duckdb")
    con = duckdb.connect(database=str(db_file_path), read_only=read_only)
    return con

# ---------------------------------------------------------------------------------------------
# Database Metadata
# ---------------------------------------------------------------------------------------------
def tablenames(con: duckdb.DuckDBPyConnection) -> List[str]:
    """
    Get list of all table names in the database.

    Args:
        con: DuckDB connection

    Returns:
        List of table names

    Example:
        >>> tablenames(con)
        ['users', 'orders', 'products']
    """
    tables = con.execute("SHOW TABLES").fetchall()
    return [table[0] for table in tables]

def columns(con: duckdb.DuckDBPyConnection) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get column information for all tables in the database.

    Args:
        con: DuckDB connection

    Returns:
        Dictionary mapping table names to lists of column dictionaries.
        Each column dict contains: 'col' (name), 'type', and 'nullable' (bool)

    Example:
        >>> columns(con)
        {
            'users': [
                {'col': 'id', 'type': 'INTEGER', 'nullable': False},
                {'col': 'name', 'type': 'VARCHAR', 'nullable': True}
            ]
        }
    """
    tables = con.execute("SHOW TABLES").fetchall()
    table_dict = {}
    for (table_name,) in tables:
        col_info = con.execute(f"DESCRIBE {table_name}").fetchall()
        columns_list = []
        for col_name, col_type, null_flag, _, _, _ in col_info:
            column_dict = {
                "col": col_name,
                "type": col_type,
                "nullable": null_flag != "NO"
            }
            columns_list.append(column_dict)

        table_dict[table_name] = columns_list

    return table_dict

def primary_keys(con: duckdb.DuckDBPyConnection) -> Dict[str, List[str]]:
    """
    Get primary key columns for all tables in the database.

    Args:
        con: DuckDB connection

    Returns:
        Dictionary mapping table names to lists of primary key column names.
        Supports compound primary keys.

    Example:
        >>> primary_keys(con)
        {'users': ['id'], 'order_items': ['order_id', 'item_id']}
    """
    pks = con.execute(_SQL_PRIMARY_KEYS).fetchall()
    pk_dict = {}
    for table_name, col_names in pks:
        pk_dict[table_name] = [col.strip() for col in col_names.split(",")]
    return pk_dict

def foreign_keys(con: duckdb.DuckDBPyConnection) -> Dict[str, List[Dict[str, List[List[str]]]]]:
    """
    Get foreign key relationships for all tables in the database.

    Args:
        con: DuckDB connection

    Returns:
        Dictionary mapping source table names to lists of foreign key relationships.
        Each relationship is a dict: {target_table: [[source_cols], [target_cols]]}
        Supports compound foreign keys.

    Example:
        >>> foreign_keys(con)
        {
            'orders': [
                {'users': [['user_id'], ['id']]}
            ],
            'order_items': [
                {'orders': [['order_id'], ['id']]},
                {'products': [['product_id'], ['id']]}
            ]
        }
    """
    fks = con.execute(_SQL_FOREIGN_KEYS).fetchall()
    fk_dict = {}
    for table_name_src, col_names_src, table_name_trg, col_names_trg in fks:
        src_cols = [col.strip() for col in col_names_src.split(",")]
        trg_cols = [col.strip() for col in col_names_trg.split(",")]
        trg_dict = {table_name_trg: [src_cols, trg_cols]}
        if table_name_src not in fk_dict:
            fk_dict[table_name_src] = [trg_dict]
        else:
            fk_dict[table_name_src].append(trg_dict)

    return fk_dict

# ---------------------------------------------------------------------------------------------
# YAML utils
# ---------------------------------------------------------------------------------------------
def schema_yaml(con):
    """
    Returns database schema as a dictionary suitable for YAML serialization.

    Args:
        con: DuckDB connection

    Returns:
        dict: Schema dictionary with structure:
            {
                'tables': [
                    {
                        'name': str,
                        'columns': [{'name': str, 'type': str, 'nullable': bool}],
                        'primary_key': [str],  # optional
                        'foreign_keys': [      # optional
                            {
                                'name': str,
                                'columns': [str],
                                'ref_table': str,
                                'ref_columns': [str]
                            }
                        ]
                    }
                ]
            }
    """
    # Get all metadata
    tables = tablenames(con)
    cols = columns(con)
    pks = primary_keys(con)
    fks = foreign_keys(con)

    schema_dict = {'tables': []}

    for table_name in tables:
        table_dict = {
            'name': table_name,
            'columns': cols.get(table_name, [])
        }

        # Add primary key if exists
        if table_name in pks:
            table_dict['primary_key'] = pks[table_name]

        # Add foreign keys if exist
        if table_name in fks:
            fk_list = []
            for fk_ref in fks[table_name]:
                # fk_ref is a dict like {'ref_table': [['src_cols'], ['trg_cols']]}
                for ref_table, (src_cols, trg_cols) in fk_ref.items():
                    fk_dict = {
                        'name': f"fk_{table_name}_{ref_table}_{'_'.join(src_cols)}",
                        'columns': src_cols,
                        'ref_table': ref_table,
                        'ref_columns': trg_cols
                    }
                    fk_list.append(fk_dict)
            table_dict['foreign_keys'] = fk_list

        schema_dict['tables'].append(table_dict)

    return schema_dict





# ---------------------------------------------------------------------------------------------
# Database info printing
# ---------------------------------------------------------------------------------------------
def tablenames_print(con: duckdb.DuckDBPyConnection) -> None:
    """
    Print all table names in the database, one per line.

    Args:
        con: DuckDB connection
    """
    tables = tablenames(con)
    print("\n".join(tables))

def columns_print(con: duckdb.DuckDBPyConnection) -> None:
    """
    Print column information for all tables in the database.

    Args:
        con: DuckDB connection
    """
    cols = columns(con)
    for table_name, col_list in cols.items():
        print(f"Table: {table_name}")
        for col in col_list:
            print(f"  {col}")  

def data_print(con: duckdb.DuckDBPyConnection, spec: Optional[Dict[str, str]] = None) -> None:
    """
    Print sample data and row counts for all tables in the database.

    Args:
        con: DuckDB connection
        spec: Optional dictionary mapping table names to column specifications.
              Use DuckDB column selection syntax (e.g., "* EXCLUDE (col1, col2)")

    Example:
        >>> spec = {"users": "* EXCLUDE (password)", "orders": "id, user_id, total"}
        >>> data_print(con, spec)
    """
    for tn in tablenames(con):
        print(f"{tn}")
        if spec is None:
            columns = "*"
        else:
            if tn in spec:
                columns = spec[tn]
            else:
                columns = "*"
        sql = f"SELECT {columns} FROM {tn} LIMIT 3;"
        print(con.sql(sql))
        sql = f"SELECT count(*) FROM {tn} LIMIT 3;"
        print(f"Number of rows: {con.sql(sql).fetchone()[0]}")
        print("\n\n")

def df_print(con: duckdb.DuckDBPyConnection, spec: Optional[Dict[str, str]] = None) -> None:
    """
    Print transposed DataFrame view of sample data and row counts for all tables.

    Args:
        con: DuckDB connection
        spec: Optional dictionary mapping table names to column specifications.
              Use DuckDB column selection syntax (e.g., "* EXCLUDE (col1, col2)")

    Example:
        >>> spec = {"users": "* EXCLUDE (password)"}
        >>> df_print(con, spec)
    """
    for tn in tablenames(con):
        print(f"{tn}")
        if spec is None:
            columns = "*"
        else:
            if tn in spec:
                columns = spec[tn]
            else:
                columns = "*"
        sql = f"SELECT {columns} FROM {tn} LIMIT 1;"
        print(con.execute(sql).df().T)
        sql = f"SELECT count(*) FROM {tn} LIMIT 3;"
        print(f"Number of rows: {con.execute(sql).fetchone()[0]}")
        print("\n\n")

def schema(con: duckdb.DuckDBPyConnection) -> str:
    """
    Generate a text representation of the database schema including foreign keys.

    Args:
        con: DuckDB connection

    Returns:
        String containing schema information with tables, columns, and foreign keys

    Example:
        >>> print(schema(con))
        Table: users (id INTEGER NOT NULL, name VARCHAR NULL)
        Table: orders (id INTEGER NOT NULL, user_id INTEGER NULL)
        Foreign Key: orders(user_id) -> users(id)
    """
    tables = con.execute("SHOW TABLES").fetchall()
    schema_str = ""
    for (table_name,) in tables:
        col_info = con.execute(f"DESCRIBE {table_name}").fetchall()
        column_defs = ", ".join(
            [
                f"{col_name} {col_type} {'NOT NULL' if null_flag == 'NO' else 'NULL'}"
                for col_name, col_type, null_flag, _, _, _ in col_info
            ]
        )
        schema_str += f"Table: {table_name} ({column_defs})\n"

    fks = con.execute(_SQL_FOREIGN_KEYS).fetchall()
    for table_name_src, col_names_src, table_name_trg, col_names_trg in fks:
        schema_str += f"Foreign Key: {table_name_src}({col_names_src}) -> {table_name_trg}({col_names_trg})\n"
    return schema_str

def schema_print(con: duckdb.DuckDBPyConnection) -> None:
    """
    Print database schema including tables, columns, and foreign keys.

    Args:
        con: DuckDB connection
    """
    schema_str = schema(con)
    print(schema_str)

def schema_yaml_print(con: duckdb.DuckDBPyConnection) -> None:
    """
    Print database schema as YAML format.

    Args:
        con: DuckDB connection
    """
    schema_dict = schema_yaml(con)
    yaml_string = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(yaml_string)

# ---------------------------------------------------------------------------------------------
# File conversion csv to parquet
# ---------------------------------------------------------------------------------------------
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

    with mem_con() as con:
        for tn in tns:
            f = p / f"{tn}.csv"
            sql_read = f"""
            create or replace table {tn} as
            select * from read_csv('{str(f)}', {spec});
            """
            con.execute(sql_read)

            if verbose:
                print(f"Table: {tn}")
                sql_print(con, f"select * from {tn} limit 2;")

            out_f = Path(out_path) / f"{tn}.parquet"
            con.execute(f"COPY (SELECT * FROM {tn}) TO '{str(out_f)}' (FORMAT 'parquet');")
