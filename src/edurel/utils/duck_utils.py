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
def duckdb_mem_con(db_path: str) -> duckdb.DuckDBPyConnection:
    schema_path = Path(db_path) / "schema.sql"
    if not schema_path.exists():
        print("No schema.sql. Creating empty in-memory database.")
    con = duckdb.connect(database=':memory:', read_only=False)
    with schema_path.open("r", encoding="utf-8") as f:
        con.execute(f.read())

    post_path = Path(db_path) / "post.sql"
    if not post_path.exists():
        print("No post.sql. Skipping post-processing.")
    with post_path.open("r", encoding="utf-8") as f:
        con.execute(f.read())
    return con

def duckdb_file_con(db_path: str) -> duckdb.DuckDBPyConnection:
    db_file_path = Path(db_path) / "db.duckdb"
    if not db_file_path.exists():
        raise ValueError("No db.duckdb.")
    con = duckdb.connect(database=str(db_file_path), read_only=True)
    return con

# ---------------------------------------------------------------------------------------------
# Database schema extraction for DuckDB
# ---------------------------------------------------------------------------------------------
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
