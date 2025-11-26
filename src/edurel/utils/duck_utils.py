import duckdb
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# Query utils
# ---------------------------------------------------------------------------------------------
def sql_print(con, sql):
    print(con.sql(sql))


def sql_df(con, sql):
    return con.sql(sql).df()

# ---------------------------------------------------------------------------------------------
# Connect to DuckDB in-memory or file-based
# ---------------------------------------------------------------------------------------------
def duckdb_mem_con(db_path: str = None, verbose: bool = False) -> duckdb.DuckDBPyConnection:
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

def duckdb_file_con(db_path: str, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    db_file_path = Path(db_path) / "db.duckdb"
    if not db_file_path.exists():
        raise ValueError("No db.duckdb.")
    con = duckdb.connect(database=str(db_file_path), read_only=read_only)
    return con

# ---------------------------------------------------------------------------------------------
# Database info
# ---------------------------------------------------------------------------------------------
def duckdb_tablenames(con):
    tables = con.execute("SHOW TABLES").fetchall()
    return [table[0] for table in tables]

def duckdb_tablenames_print(con):
    tables = duckdb_tablenames(con)
    print("\n".join(tables))

# example spec:
# spec = {
#     "DimCustomer": "* exclude (NameStyle, SpanishEducation)"
# }
# 
def duckdb_data_print(con, spec: dict = None):
    for tn in  duckdb_tablenames(con):
        print(f"{tn}")
        if spec is  None:
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

def duckdb_df_print(con, spec: dict = None):
    for tn in  duckdb_tablenames(con):
        print(f"{tn}")
        if spec is  None:
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

def duckdb_schema(con):
    tables = con.execute("SHOW TABLES").fetchall()
    schema = ""
    for (table_name,) in tables:
        columns = con.execute(f"DESCRIBE {table_name}").fetchall()
        column_defs = ", ".join(
            [
                f"{col_name} {col_type} {'NOT NULL' if nvl == 'NO' else 'NULL'}"
                for col_name, col_type, nvl, _, _, _ in columns
            ]
        )
        schema += f"Table: {table_name} ({column_defs})\n"

    sql = """
      select
        table_name as table_name_src,
        list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names_src,
        referenced_table as table_name_trg,
        list_aggregate(referenced_column_names, 'string_agg', ', ') as col_names_trg,
      from duckdb_constraints() where constraint_type = 'FOREIGN KEY';
  """

    fks = con.execute(sql).fetchall()
    for table_name_src, col_names_src, table_name_trg, col_names_trg in fks:
        schema += f"Foreign Key: {table_name_src}({col_names_src}) -> {table_name_trg}({col_names_trg})\n"
    return schema

def duckdb_schema_print(con):
    schema = duckdb_schema(con)
    print(schema)


# ---------------------------------------------------------------------------------------------
# Read multiple files into DuckDB tables. Exports to Parquet if out_path is provided
# ---------------------------------------------------------------------------------------------
def db_file_op(in_path: str, fn: str, suffix: str, spec: str, show: bool = False, out_path: str = None):
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
    if len(files) == 0:
        raise ValueError(f"No files found in {in_path} with fn={fn} and suffix={suffix}")
    
    with duckdb_mem_con() as con:
        for tn in tns:
            f = p / f"{tn}{suffix}"
            sql_read = f"""
            create or replace table {tn} as
            select * from read_csv('{str(f)}', {spec});
            """
            con.execute(sql_read)
    
            if show is not None:
                print(f"Table: {tn}")
                sql_print(con, f"select * from {tn} limit 2;")
    
            if out_path is not None:
                out_f = Path(out_path) / f"{tn}.parquet"
                con.execute(f"COPY (SELECT * FROM {tn}) TO '{str(out_f)}' (FORMAT 'parquet');")
