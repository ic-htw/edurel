import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import yaml
import pandas as pd

# ---------------------------------------------------------------------------------------------
# Query utils
# ---------------------------------------------------------------------------------------------
def sql_print(con, sql):
    cur = con.cursor()
    rows = cur.execute(sql).fetchall()
    for row in rows:
        print(row)

def sql_df(con, sql):
    df = pd.read_sql_query(sql, con)
    return df

# ---------------------------------------------------------------------------------------------
# Connection utils
# ---------------------------------------------------------------------------------------------
def file_con(db_path):
    con = sqlite3.connect(db_path)
    return con

# ---------------------------------------------------------------------------------------------
# Database Metadata
# ---------------------------------------------------------------------------------------------
def tablenames(con):
    sql = "SELECT name FROM sqlite_master WHERE type='table';"
    cur = con.cursor()
    tables = cur.execute(sql).fetchall()
    return [table[0] for table in tables]

def columns(con, tablename):
    sql = f"PRAGMA table_info('{tablename}')"
    cols = pd.read_sql_query(sql, con)[['name', 'type', 'notnull', 'pk']]
    return cols.to_dict(orient='records')


# ---------------------------------------------------------------------------------------------
# YAML utils
# ---------------------------------------------------------------------------------------------
def schema_yaml(con):
    tables = tablenames(con)

    schema_dict = {}
    for tablename in tables:
        schema_dict[tablename] = columns(con, tablename)
    return schema_dict


# ---------------------------------------------------------------------------------------------
# Database info printing
# ---------------------------------------------------------------------------------------------
def tablenames_print(con):
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

def schema(con):
    tables = tablenames(con)
    schema_str = ""
    for tablename in tables:
        cols = [f"{c['name']} {c['type']} {'NOT NULL' if c['notnull'] == 1 else 'NULL'}" for c in columns(con, tablename)]
        column_defs = ", ".join(cols)
        schema_str += f"Table: {tablename} ({column_defs})\n"
    return schema_str

def schema_print(con):
    schema_str = schema(con)
    print(schema_str)

def schema_yaml_print(con):
    schema_dict = schema_yaml(con)
    yaml_string = yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)
    print(yaml_string)

