from typing import Dict, List, Any, Optional
import duckdb
import pandas as pd
import subprocess
import tempfile
from pathlib import Path
import yaml



class Db:
    def __init__(self, con: duckdb.DuckDBPyConnection, db_file_path: Optional[str] = None):
        self.con = con
        self.db_file_path = db_file_path

    @classmethod
    def mem(cls) -> 'Db':
        """Create Db instance with in-memory DuckDB connection.

        Returns:
            Db instance with in-memory connection

        Example:
            >>> db = Db.mem()
            >>> db.exe("CREATE TABLE users (id INTEGER PRIMARY KEY);")
        """
        con = duckdb.connect(database=':memory:', read_only=False)
        return cls(con, db_file_path=None)

    @classmethod
    def file(cls, db_file_path: str, read_only: bool = True) -> 'Db':
        """Create Db instance with file-based DuckDB connection.

        Args:
            db_file_path: Path to DuckDB database file
            read_only: If True, opens database in read-only mode. Default is True.

        Returns:
            Db instance with file-based connection

        Example:
            >>> db = Db.file("my_database.duckdb")
            >>> db = Db.file("my_database.duckdb", read_only=False)
        """
        con = duckdb.connect(database=str(db_file_path), read_only=read_only)
        return cls(con, db_file_path=str(db_file_path))

    def exe(self, sql: str) -> None:
        self.con.execute(sql)

    def file_exe(self, sql_file_path: str) -> None:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
            self.con.execute(sql)

    def eval(self, sql: str) -> str:
        return str(self.con.sql(sql))

    def eval_nx(self, sql: str) -> str:
        try: 
            return str(self.con.sql(sql))
        except Exception as e:
            return f"err: {str(e)}"

    def eval_file(self, sql_file_path: str) -> str:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        return self.eval(sql)

    def eval_df(self, sql: str) -> pd.DataFrame:
        return self.con.sql(sql).df()
 
    def eval_file_df(self, sql_file_path: str) -> pd.DataFrame:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        return self.eval_df(sql)

    def print(self, sql: str) -> None:
        print(self.eval(sql))

    def print_into_file(self, sql: str, sql_file_path: str) -> None:
        with open(sql_file_path, "w", encoding="utf-8") as f:
            f.write(self.eval(sql))

    def dbname(self) -> Optional[str]:
        """Extract database name (filename without suffix) from db_file_path.

        Returns:
            Database name (filename without extension) if db_file_path is set,
            None for in-memory databases
        """
        if self.db_file_path is None:
            return None
        return Path(self.db_file_path).stem

    def tablenames(self) -> List[str]:
        """Get list of all table names in the database.

        Returns:
            List of table names
        """
        tables = self.con.execute("SHOW TABLES").fetchall()
        return [table[0] for table in tables]

    def columns(self, tablename: str) -> List[Dict[str, Any]]:
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

    def primary_keys(self, tablename: str) -> List[str]:
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

    def foreign_keys(self, tablename: str) -> List[Dict[str, List[List[str]]]]:
        """Get foreign key relationships for a specific table in the database.

        Args:
            tablename: Name of the table

        Returns:
            List of fk dicts for the specified table.
            Each relationship is a dict: {target_table: [[source_cols], [target_cols]]}

        Example:
            >>> db.foreign_keys('orders')
            [{'users': [['user_id'], ['id']]}]
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

    def yaml(self) -> str:
        """Generate YAML representation of the database schema.

        Returns:
            YAML string representing the complete database schema with tables,
            columns, primary keys, and foreign keys

        Example:
            >>> db = Db.mem()
            >>> db.exe("CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR);")
            >>> yaml_str = db.yaml()
            >>> print(yaml_str)
        """
        tables_list = []

        for tablename in self.tablenames():
            table_dict = {
                "tablename": tablename,
                "columns": self.columns(tablename)
            }

            # Add primary keys if they exist
            pks = self.primary_keys(tablename)
            if pks:
                table_dict["primary_key"] = pks

            # Add foreign keys if they exist
            fks_raw = self.foreign_keys(tablename)
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