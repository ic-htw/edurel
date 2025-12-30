import duckdb
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import yaml
import pandas as pd

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
def mem_con1(db_path: Optional[str] = None, verbose: bool = False) -> duckdb.DuckDBPyConnection:
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

def exe_sql_file(con: duckdb.DuckDBPyConnection, sql_file_path: str) -> None:
    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql = f.read()
    con.execute(sql)

def con_mem() -> duckdb.DuckDBPyConnection:
    """
    Connect to an empty in-memory DuckDB database.

    Returns:
        DuckDB connection to the database file

    """
    con = duckdb.connect(database=':memory:', read_only=False)
    return con

def con_file(db_file_path: str, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """
    Connect to a persistent DuckDB database file.

    Args:
        db_file_path: Path to duckdb file
        read_only: If True, opens database in read-only mode, otherwise create empty db

    Returns:
        DuckDB connection to the database file

    """
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
    """
    tables = con.execute("SHOW TABLES").fetchall()
    return [table[0] for table in tables]

def columns(con: duckdb.DuckDBPyConnection, tablename: str) -> List[Dict[str, Any]]:
    """
    Get column information for a specific table in the database.

    Args:
        con: DuckDB connection
        tablename: Name of the table to describe

    Returns:
        List of column dicts for the specified table.
        Each column dict contains: 'columnname', 'type', and 'nullable' (bool)
    """
    col_info = con.execute(f"DESCRIBE {tablename}").fetchall()
    columns_list = []
    for col_name, col_type, null_flag, _, _, _ in col_info:
        column_dict = {
            "columnname": col_name,
            "type": col_type,
            "nullable": null_flag != "NO"
            }
        columns_list.append(column_dict)
    return columns_list

def primary_keys(con: duckdb.DuckDBPyConnection, tablename: str) -> List[str]:
    """
    Get primary key columns for a specific table in the database.

    Args:
        con: DuckDB connection

    Returns:
         List of primary columns for the specified table.
    """

    sql = f"""
    SELECT
      list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names
    FROM duckdb_constraints()
    WHERE constraint_type = 'PRIMARY KEY' AND lcase(table_name) = lcase('{tablename}');
    """    

    pks = con.execute(sql).fetchone()
    return pks[0].split(", ") if pks and pks[0] is not None else []

def foreign_keys(con: duckdb.DuckDBPyConnection, tablename: str) -> List[Dict[str, List[List[str]]]]:
    """
    Get foreign key relationships for a specific table in the database.

    Args:
        con: DuckDB connection

    Returns:
        List of fk dicts for the specified table.
        Each relationship is a dict: {target_table: [[source_cols], [target_cols]]}

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

    sql = f"""
    SELECT
      list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names_src,
      referenced_table as table_name_trg,
      list_aggregate(referenced_column_names, 'string_agg', ', ') as col_names_trg
    FROM duckdb_constraints()
    WHERE constraint_type = 'FOREIGN KEY' AND lcase(table_name) = lcase('{tablename}');
    """

    fks = con.execute(sql).fetchall()
    fk_list = []
    for col_names_src, table_name_trg, col_names_trg in fks:
        src_cols = [col.strip() for col in col_names_src.split(",")]
        trg_cols = [col.strip() for col in col_names_trg.split(",")]
        trg_dict = {table_name_trg: [src_cols, trg_cols]}
        fk_list.append(trg_dict)

    return fk_list

def to_fk_dict(fk_str: str) -> Dict[str, List[List[str]]]:
    """
    Helper function to create foreign key dictionary.

    Args:
        fk_str: Foreign key string in the format 'targettable|sourcecolumns|targetcolumns'

    Returns:
        Dict representing the foreign key relationship
    """
    parts = fk_str.split("|")
    if len(parts) != 3:
        raise ValueError("fk_str must be in the format 'targettable|sourcecolumns|targetcolumns'")
    targettable = parts[0]
    sourcecolumns = [col.strip() for col in parts[1].split(",")]
    targetcolumns = [col.strip() for col in parts[2].split(",")]   
    return {targettable: [sourcecolumns, targetcolumns]}

# ---------------------------------------------------------------------------------------------
# YAML utils
# ---------------------------------------------------------------------------------------------
def schema_yaml(con: duckdb.DuckDBPyConnection, additional_fks: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Returns database schema as a dictionary suitable for YAML serialization.

    Args:
        con: DuckDB connection
        aditional_fks: Dict of additional foreign keys to include in the schema
     """

    tables = tablenames(con)

    schema_dict = {'tables': []}

    for tablename in tables:
        table_dict = {
            'tablename': tablename,
            'columns': columns(con, tablename)
        }

        pks = primary_keys(con, tablename)
        if pks:
            table_dict['primary_key'] = pks

        fks = foreign_keys(con, tablename)
        fks += [to_fk_dict(fk_str) for fk_str in additional_fks.get(tablename, [])]
        if fks:
            fk_list = []
            for fk_ref in fks:
                n = 1
                # fk_ref is a dict like {'ref_table': [['src_cols'], ['trg_cols']]}
                for ref_table, (src_cols, trg_cols) in fk_ref.items():
                    fk_dict = {
                        'fkname': f"fk_{tablename}_{ref_table}_{'_'.join(src_cols)}_{n}",
                        'sourcecolumns': src_cols,
                        'targettable': ref_table,
                        'targetcolumns': trg_cols
                    }
                    fk_list.append(fk_dict)
                n += 1
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

def schema_yaml_print(con: duckdb.DuckDBPyConnection, additional_fks: Dict[str, List[str]]) -> None:
    """
    Print database schema as YAML format.

    Args:
        con: DuckDB connection
        additional_fks: Dict of additional foreign keys to include in the schema
    """
    schema_dict = schema_yaml(con, additional_fks)
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
