import os
import edurel.utils.duckdb as ddbu

def company_en():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_mem()
    SQL_DIR = f"{DB_DIR}/company_en"
    ddbu.exe_sql_file(con, f"{SQL_DIR}/schema.sql")
    ddbu.exe_sql_file(con, f"{SQL_DIR}/data.sql")
    return con