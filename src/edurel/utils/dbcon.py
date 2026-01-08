import os
import edurel.utils.duckdb as ddbu

def adw_olap():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_file(f"{DB_DIR}/adw-olap/adw-olap.duckdb")
    return con

def adw_oltp():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_file(f"{DB_DIR}/adw-oltp/adw-oltp.duckdb")
    return con

def ccfraud():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_file(f"{DB_DIR}/ccfraud/ccfraud.duckdb")
    return con

def company_de():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_mem()
    SQL_DIR = f"{DB_DIR}/company_de"
    ddbu.exe_sql_file(con, f"{SQL_DIR}/schema.sql")
    ddbu.exe_sql_file(con, f"{SQL_DIR}/data.sql")
    return con

def company_en():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_mem()
    SQL_DIR = f"{DB_DIR}/company_en"
    ddbu.exe_sql_file(con, f"{SQL_DIR}/schema.sql")
    ddbu.exe_sql_file(con, f"{SQL_DIR}/data.sql")
    return con

def foodmart():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    con = ddbu.con_file(f"{DB_DIR}/foodmart/foodmart.duckdb")
    return con

