from datetime import date, datetime, time
from decimal import Decimal
import math
import re
from typing import Dict, List, Any, Optional
from uuid import UUID
import duckdb
import pandas as pd
from pathlib import Path
import yaml

from edurel.utils.misc import save_from_url

class DuckDbMan:
    def __init__(self, con: duckdb.DuckDBPyConnection, db_file_path: Optional[str] = None, db_name: Optional[str] = None):
        self.con = con
        self.db_file_path = db_file_path

        if self.db_file_path:
            self.name = Path(self.db_file_path).stem
        elif db_name:
            self.name = db_name
        else:
            raise ValueError("Either db_file_path or db_name must be provided")

    @classmethod
    def fromMem(cls, db_name: Optional[str] = None) -> 'DuckDbMan':
        """Create Db instance with in-memory DuckDB connection.

        Returns:
            Db instance with in-memory connection
        """
        con = duckdb.connect(database=':memory:', read_only=False)
        if not db_name:
            db_name = "dummy_db"
        return cls(con, db_file_path=None, db_name=db_name)

    @classmethod
    def fromFile(cls, db_file_path: str|Path, read_only: bool = True) -> 'DuckDbMan':
        """Create Db instance with file-based DuckDB connection.

        Args:
            db_file_path: Path to DuckDB database file
            read_only: If True, opens database in read-only mode. Default is True.

        Returns:
            Db instance with file-based connection
        """
        con = duckdb.connect(database=str(db_file_path), read_only=read_only)
        return cls(con, db_file_path=str(db_file_path))

    @classmethod
    def fromURL(
        cls,
        db_file: str,
        base_url: str,
        save_dir: str | Path,
        read_only: bool = True,
        overwrite: bool = False,
    ) -> 'DuckDbMan':
        """Download a DuckDB database file and open a connection to the saved copy.

        Args:
            db_file: Database filename to download from base_url
            base_url: Base URL hosting the database file
            save_dir: Directory where the database file should be saved
            read_only: If True, opens database in read-only mode. Default is True.
            overwrite: If True, overwrite an existing saved database file. Default is False.

        Returns:
            Db instance with file-based connection to the saved database
        """
        url = f"{str(base_url).rstrip('/')}/{db_file}"
        save_from_url(db_file, url, str(save_dir), overwrite=overwrite)
        db_file_path = Path(save_dir) / db_file
        return cls.fromFile(db_file_path, read_only=read_only)

    def close(self) -> None:
        self.con.close()

    def execute(self, sql: str) -> None:
        self.con.execute(sql)

    def execute_file(self, sql_file_path: str) -> None:
        sql = Path(sql_file_path).read_text(encoding="utf-8")
        self.con.execute(sql)

    def sql(self, sql: str) -> str:
        return str(self.con.sql(sql))

    def sql_nx(self, sql: str) -> str:
        try: 
            return str(self.con.sql(sql))
        except Exception as e:
            return f"err: {str(e)}"

    def sql_file(self, sql_file_path: str) -> str:
        sql = Path(sql_file_path).read_text(encoding="utf-8")
        return self.sql(sql)

    def sql_df(self, sql: str) -> pd.DataFrame:
        return self.con.sql(sql).df()
 
    def sql_file_df(self, sql_file_path: str) -> pd.DataFrame:
        sql = Path(sql_file_path).read_text(encoding="utf-8")
        return self.sql_df(sql)

    def print(self, sql: str) -> None:
        print(self.sql(sql))

    def get_tablenames(self) -> List[str]:
        """Get list of all table names in the database.

        Returns:
            List of table names
        """
        tables = self.con.execute("SHOW TABLES").fetchall()
        return [table[0] for table in tables]

    def get_columns(self, tablename: str) -> List[Dict[str, Any]]:
        """Get column information for a specific table in the database.

        Args:
            tablename: Name of the table to describe

        Returns:
            List of column dicts for the specified table.
            Each column dict contains: 'columnname', 'type', and 'nullable' (bool)
        """
        col_info = self.con.execute(f"DESCRIBE {tablename}").fetchall()
        columns_list = []
        for col_name, col_type, null_flag, _, _, _ in col_info:
            column_dict = {
                "columnname": col_name,
                "type": col_type,
                "nullable": null_flag != "NO"
            }
            columns_list.append(column_dict)
        return columns_list

    def get_primary_keys(self, tablename: str) -> List[str]:
        """Get primary key columns for a specific table in the database.

        Args:
            tablename: Name of the table

        Returns:
            List of primary key columns for the specified table
        """
        sql = f"""
        SELECT
          list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names
        FROM duckdb_constraints()
        WHERE constraint_type = 'PRIMARY KEY' AND lcase(table_name) = lcase('{tablename}');
        """

        pks = self.con.execute(sql).fetchone()
        return pks[0].split(", ") if pks and pks[0] is not None else []

    def get_foreign_keys(self, tablename: str) -> List[Dict[str, List[List[str]]]]:
        """Get foreign key relationships for a specific table in the database.

        Args:
            tablename: Name of the table

        Returns:
            List of fk dicts for the specified table.
            Each relationship is a dict: {target_table: [[source_cols], [target_cols]]}
        """
        sql = f"""
        SELECT
          list_aggregate(constraint_column_names, 'string_agg', ', ') as col_names_src,
          referenced_table as table_name_trg,
          list_aggregate(referenced_column_names, 'string_agg', ', ') as col_names_trg
        FROM duckdb_constraints()
        WHERE constraint_type = 'FOREIGN KEY' AND lcase(table_name) = lcase('{tablename}');
        """

        fks = self.con.execute(sql).fetchall()
        fk_list = []
        for col_names_src, table_name_trg, col_names_trg in fks:
            src_cols = [col.strip() for col in col_names_src.split(",")]
            trg_cols = [col.strip() for col in col_names_trg.split(",")]
            trg_dict = {table_name_trg: [src_cols, trg_cols]}
            fk_list.append(trg_dict)

        return fk_list

    def get_yaml(self) -> str:
        """Generate YAML representation of the database schema.

        Returns:
            YAML string representing the complete database schema with tables,
            columns, primary keys, and foreign keys
        """
        tables_list = []

        for tablename in self.get_tablenames():
            table_dict = {
                "tablename": tablename,
                "columns": self.get_columns(tablename)
            }

            # Add primary keys if they exist
            pks = self.get_primary_keys(tablename)
            if pks:
                table_dict["primary_key"] = pks

            # Add foreign keys if they exist
            fks_raw = self.get_foreign_keys(tablename)
            if fks_raw:
                fks_formatted = []
                for idx, fk_dict in enumerate(fks_raw, start=1):
                    # Extract target table and columns from the dict
                    target_table = list(fk_dict.keys())[0]
                    source_cols, target_cols = fk_dict[target_table]

                    # Generate foreign key name
                    first_source_col = source_cols[0] if source_cols else "unknown"
                    fkname = f"fk_{tablename}_{target_table}_{first_source_col}_{idx}"

                    fk_formatted = {
                        "fkname": fkname,
                        "sourcecolumns": source_cols,
                        "targettable": target_table,
                        "targetcolumns": target_cols
                    }
                    fks_formatted.append(fk_formatted)

                table_dict["foreign_keys"] = fks_formatted

            tables_list.append(table_dict)

        schema_dict = {"tables": tables_list}

        # Convert to YAML string with proper formatting
        return yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)

    def export_data_as_insert_statements(self, for_tables: List[str]) -> str:
        """Export data from specified tables as SQL insert statements."""
        def sql_identifier(identifier: str) -> str:
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
                return identifier
            return '"' + identifier.replace('"', '""') + '"'

        def sql_literal(value: Any) -> str:
            if value is None:
                return "NULL"
            if isinstance(value, bool):
                return "TRUE" if value else "FALSE"
            if isinstance(value, str):
                return "'" + value.replace("'", "''") + "'"
            if isinstance(value, (int, Decimal)):
                return str(value)
            if isinstance(value, float):
                if math.isnan(value):
                    return "CAST('NaN' AS DOUBLE)"
                if math.isinf(value):
                    inf = "Infinity" if value > 0 else "-Infinity"
                    return f"CAST('{inf}' AS DOUBLE)"
                return repr(value)
            if isinstance(value, datetime):
                return "'" + value.isoformat(sep=" ") + "'"
            if isinstance(value, date):
                return "'" + value.isoformat() + "'"
            if isinstance(value, time):
                return "'" + value.isoformat() + "'"
            if isinstance(value, UUID):
                return f"'{value}'"
            if isinstance(value, bytes):
                return f"from_hex('{value.hex()}')"
            try:
                if pd.isna(value):
                    return "NULL"
            except TypeError:
                pass
            raise TypeError(f"Unsupported value type for SQL export: {type(value)!r}")

        statements: list[str] = []

        for index, table_name in enumerate(for_tables):
            table_sql = sql_identifier(table_name)
            result = self.con.execute(f"SELECT * FROM {table_sql}")
            rows = result.fetchall()
            columns = [sql_identifier(column[0]) for column in result.description]
            columns_sql = ", ".join(columns)

            if index > 0:
                statements.append("")
            statements.append(f"-- Table: {table_name}")
            for row in rows:
                values_sql = ", ".join(sql_literal(value) for value in row)
                statements.append(
                    f"INSERT INTO {table_sql} ({columns_sql}) VALUES ({values_sql});"
                )

        return "\n".join(statements)
