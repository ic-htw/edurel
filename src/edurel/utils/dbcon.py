import os
from edurel.utils.duckdb import Db

def adw_olap():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.file(f"{DB_DIR}/adw-olap/adw-olap.duckdb")
    return db

def adw_etl():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.mem()
    SQL_DIR = f"{DB_DIR}/adw-etl"
    db.file_exe(f"{SQL_DIR}/schema.sql")
    return db

def adw_oltp():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.file(f"{DB_DIR}/adw-oltp/adw-oltp.duckdb")
    return db

def ccfraud():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.file(f"{DB_DIR}/ccfraud/ccfraud.duckdb")
    return db

def company_de():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.mem()
    SQL_DIR = f"{DB_DIR}/company_de"
    db.file_exe(f"{SQL_DIR}/schema.sql")
    db.file_exe(f"{SQL_DIR}/data.sql")
    return db

def company_en():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.mem()
    SQL_DIR = f"{DB_DIR}/company_en"
    db.file_exe(f"{SQL_DIR}/schema.sql")
    db.file_exe(f"{SQL_DIR}/data.sql")
    return db

def foodmart():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.file(f"{DB_DIR}/foodmart/foodmart.duckdb")
    return db

def playlist_de():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.mem()
    SQL_DIR = f"{DB_DIR}/playlist_de"
    db.file_exe(f"{SQL_DIR}/schema.sql")
    db.file_exe(f"{SQL_DIR}/data.sql")
    return db

def playlist_en():
    DB_DIR = f"{os.getenv("BASE_DIR")}/databases"
    db = Db.mem()
    SQL_DIR = f"{DB_DIR}/playlist_en"
    db.file_exe(f"{SQL_DIR}/schema.sql")
    db.file_exe(f"{SQL_DIR}/data.sql")
    return db

