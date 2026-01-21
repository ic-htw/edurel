"""
Database Handler

A class for managing DuckDB database operations with schema visualization support.
"""
from typing import Dict, List, Any, Optional
import duckdb
import pandas as pd
import subprocess
import tempfile
from pathlib import Path

from . import duckdb as duckdb_utils
from . import yaml_utils


class DbHandler:
    """
    A handler class for DuckDB database operations.

    Provides convenient methods for executing queries, managing schemas,
    and generating visualizations.
    """

    def __init__(self, con: duckdb.DuckDBPyConnection, additional_fks: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the DbHandler.

        Args:
            con: DuckDB connection
            additional_fks: Dict mapping table names to lists of additional foreign key strings
                           not present in the database metadata
        """
        self.con = con
        self.additional_fks = additional_fks if additional_fks is not None else {}

    def schema_yaml_dict(self, omit_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get database schema as a YAML dictionary.

        Args:
            omit_tags: List of keys to omit from the schema

        Returns:
            Dictionary representing the database schema
        """
        # Get schema with additional foreign keys
        schema_dict = duckdb_utils.schema_yaml(self.con, self.additional_fks)

        # Remove specified tags if provided
        if omit_tags:
            schema_dict = yaml_utils.yaml_remove_tags(schema_dict, omit_tags)

        return schema_dict

    def schema_yaml_str(self, omit_tags: Optional[List[str]] = None) -> str:
        """
        Get database schema as a YAML string.

        Args:
            omit_tags: List of keys to omit from the schema

        Returns:
            Yaml string representing the database schema
        """
        # Get schema with additional foreign keys
        schema_dict = self.schema_yaml_dict(omit_tags)

        # Remove specified tags if provided
        if omit_tags:
            schema_dict = yaml_utils.yaml_remove_tags(schema_dict, omit_tags)

        return yaml_utils.yaml.dump(schema_dict, default_flow_style=False, sort_keys=False)

    def schema_yaml_print(self, omit_tags: Optional[List[str]] = None) -> None:
        """
        Print database schema as a YAML.

        Args:
            omit_tags: List of keys to omit from the schema
        """
        print(self.schema_yaml_str(omit_tags))

    def schema_mermaid(self, omit_tags: Optional[List[str]] = None, direction="TB") -> str:
        """
        Get database schema as Mermaid ER diagram code.

        Args:
            omit_tags: List of keys to omit from the schema

        Returns:
            String containing Mermaid ER diagram code
        """
        # Get schema YAML
        schema_dict = self.schema_yaml_dict(omit_tags)

        # Convert to Mermaid
        mermaid_code = yaml_utils.yaml_to_mermaid(schema_dict, direction)

        return mermaid_code

    def schema_mermaid_png(
        self,
        output_path: str,
        omit_tags: Optional[List[str]] = None,
        direction: str = "TB",
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: float = 1.0
    ) -> None:
        """
        Save database schema as a PNG file using Mermaid diagram.

        Args:
            output_path: Path where the PNG file should be saved
            omit_tags: List of keys to omit from the schema
            direction: Diagram direction (TB, LR, etc.)
            width: Width of the viewport in pixels (optional, auto-sizes if not specified)
            height: Height of the viewport in pixels (optional, auto-sizes if not specified)
            scale: Scale factor for the output image (default: 1.0, use 2.0 or 3.0 for higher resolution)

        Raises:
            FileNotFoundError: If mmdc (mermaid-cli) is not installed
            subprocess.CalledProcessError: If mmdc conversion fails

        Example:
            # Generate a high-resolution diagram
            handler.schema_mermaid_png("schema.png", scale=3.0)

            # Generate a diagram with specific dimensions
            handler.schema_mermaid_png("schema.png", width=2400, height=1800)
        """
        # Get Mermaid code
        mermaid_code = self.schema_mermaid(omit_tags, direction)

        # Create a temporary file for the Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp_file:
            tmp_file.write(mermaid_code)
            tmp_mmd_path = tmp_file.name

        try:
            # Build mmdc command
            cmd = ['mmdc', '-i', tmp_mmd_path, '-o', output_path]

            # Add optional parameters
            if width is not None:
                cmd.extend(['-w', str(width)])
            if height is not None:
                cmd.extend(['-H', str(height)])
            if scale != 1.0:
                cmd.extend(['-s', str(scale)])

            # Convert to PNG using mmdc (mermaid-cli)
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "mermaid-cli (mmdc) is not installed. "
                    "Install it with: npm install -g @mermaid-js/mermaid-cli"
                ) from None
        finally:
            # Clean up temporary file
            Path(tmp_mmd_path).unlink(missing_ok=True)

    def sql_exe(self, sql: str) -> None:
        """
        Execute SQL code on the database connection.

        Args:
            sql: SQL code to execute
        """
        self.con.execute(sql)

    def sql_file_exe(self, sql_file_path: str) -> None:
        """
        Execute SQL code from a file on the database connection.

        Args:
            sql_file_path: Path to SQL file
        """
        duckdb_utils.exe_sql_file(self.con, sql_file_path)

    def sql_df(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query and return result as a pandas DataFrame.

        Args:
            sql: SQL query to execute

        Returns:
            pandas DataFrame containing query results
        """
        return duckdb_utils.sql_df(self.con, sql)

    def sql_file_df(self, sql_file_path: str) -> pd.DataFrame:
        """
        Execute SQL query from a file and return result as a pandas DataFrame.

        Args:
            sql_file_path: Path to SQL file containing query

        Returns:
            pandas DataFrame containing query results
        """
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        return self.sql_df(sql)

    def sql_str(self, sql: str) -> None:
        """
        Execute SQL query and return the result.

        Args:
            sql: SQL query to execute
        """
        return duckdb_utils.sql_str(self.con, sql)

    def sql_print(self, sql: str) -> None:
        """
        Execute SQL query and print the result.

        Args:
            sql: SQL query to execute
        """
        duckdb_utils.sql_print(self.con, sql)

    def sql_file_print(self, sql_file_path: str) -> None:
        """
        Execute SQL query from a file and print the result.

        Args:
            sql_file_path: Path to SQL file containing query
        """
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        self.sql_out(sql)
