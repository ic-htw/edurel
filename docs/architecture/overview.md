# DuckDB Handling
- con_file(db_file_path: str, read_only: bool = True)
- con_mem() 
- exe_sql_file(con: duckdb.DuckDBPyConnection, sql_file_path: str) 

# DuckDB Metadata
- tablenames(con: duckdb.DuckDBPyConnection) -> List[str]
- columns(con: duckdb.DuckDBPyConnection, tablename: str) -> List[Dict[str, Any]]
- primary_keys(con: duckdb.DuckDBPyConnection, tablename: str) -> List[str]:
- oreign_keys(con: duckdb.DuckDBPyConnection, tablename: str) -> List[Dict[str, List[List[str]]]]
- to_fk_dict(targettable, sourcecolumns, targetcolumns) -> Dict[str, List[List[str]]]

# DuckDB -> yamldict
- schema_yaml(con: duckdb.DuckDBPyConnection, additional_fks: Dict[str, List[str]]) -> Dict[str, Any]

# Printing
- schema_yaml_print(con: duckdb.DuckDBPyConnection, additional_fks: Dict[str, List[str]]) -> None