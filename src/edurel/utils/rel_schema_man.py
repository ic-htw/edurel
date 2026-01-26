import re
import yaml
from fnmatch import fnmatch
from typing import Any, Dict, List, Optional
import subprocess
import tempfile
from pathlib import Path


class RelSchemaMan:
    def __init__(self, yaml_str: str):
        import copy
        self.yaml_base_dict = yaml.safe_load(yaml_str)
        self.yaml_dict = copy.deepcopy(self.yaml_base_dict)

    def transform(self, spec_file_path: str) -> None:
        """Transform YAML schema input according to specification from YAML file.

        Args:
            spec_file_path: Path to YAML file containing transformation steps

        Side effects:
            Modifies self.yaml_dict in place

        YAML file format:
            transformation_steps:
            - del table pattern:<pattern>
            - del table index:<index_spec>
            - del column <table> pattern:<pattern>

        Transformation language:
            del table pattern:<pattern>              - Delete tables matching pattern
            del table index:<index_spec>             - Delete tables by index
            del column <table> pattern:<pattern>     - Delete columns in table matching pattern
            del column <table> index:<index_spec>    - Delete columns in table by index
            del column * pattern:<pattern>           - Delete columns matching pattern in all tables
            del fk pattern:<pattern>                 - Delete foreign keys matching pattern
            del fk index:<index_spec>                - Delete foreign keys by index

        Index spec formats:
            0           - Single index
            [0,2,4]     - List of indexes
            [1:5]       - Slice
            [::2]       - Slice with step
            [1:3,5:7]   - Multiple slices/indexes

        Example:
            >>> sman = RelSchemaMan(yaml_str)
            >>> sman.transform("path/to/transforms.yaml")
        """
        # Read YAML file
        with open(spec_file_path, 'r') as f:
            transform_data = yaml.safe_load(f)

        # Extract transformation_steps list
        if not isinstance(transform_data, dict) or 'transformation_steps' not in transform_data:
            raise ValueError(f"YAML file must contain 'transformation_steps' key with list of steps")

        transformation_steps = transform_data['transformation_steps']
        if not isinstance(transformation_steps, list):
            raise ValueError(f"'transformation_steps' must be a list")

        # Process each transformation step
        for step in transformation_steps:
            if not step or isinstance(step, str) and step.strip().startswith('#'):
                continue
            step = step.strip()
            self.yaml_dict = self._apply_transformation(self.yaml_dict, step)

    def yaml(self) -> str:
        """Convert yaml_dict to YAML string format.

        Returns:
            YAML string representation of yaml_dict
        """
        return yaml.dump(self.yaml_dict, default_flow_style=False, sort_keys=False)

    def yaml_base(self) -> str:
        """Convert yaml_base_dict to YAML string format.

        Returns:
            YAML string representation of yaml_base_dict
        """
        return yaml.dump(self.yaml_base_dict, default_flow_style=False, sort_keys=False)

    def mermaid(self, direction: str = "TB") -> str:
        """Convert yaml_dict to Mermaid ER diagram code.

        Args:
            direction: Diagram direction (TB, LR, RL, BT). Default is "TB" (top-to-bottom)

        Returns:
            String containing Mermaid ER diagram code

        Example:
            >>> sman = SMan(yaml_str)
            >>> mermaid_code = sman.mermaid()
            >>> mermaid_code = sman.mermaid(direction="LR")
        """
        lines = ["erDiagram"]
        lines.append(f"    direction {direction}")
        tables = self.yaml_dict.get("tables", [])

        # Generate table definitions
        for table in tables:
            tablename = table["tablename"]
            columns = table.get("columns", [])
            pk_cols = set(table.get("primary_key", []))

            lines.append(f"    {tablename} {{")
            for col in columns:
                columnname = col["columnname"]
                col_type = col["type"]
                # Remove size indicators like (9,2) or (255)
                col_type = re.sub(r"\([^)]*\)", "", col_type)

                # Add PK marker if column is in primary key
                constraint = " PK" if columnname in pk_cols else ""
                lines.append(f"        {col_type} {columnname}{constraint}")
            lines.append("    }")

        # Generate relationships from foreign keys
        for table in tables:
            tablename = table["tablename"]
            foreign_keys = table.get("foreign_keys", [])
            for fk in foreign_keys:
                targettable = fk["targettable"]
                sourcecolumns = ", ".join(fk["sourcecolumns"])
                targetcolumns = ", ".join(fk["targetcolumns"])
                # Mermaid relationship: many-to-one
                lines.append(
                    f'    {tablename} }}o--|| {targettable} : "{sourcecolumns} -> {targetcolumns}"'
                )

        return "\n".join(lines)

    def save_mermaid_png(
        self,
        output_path: str,
        direction: str = "TB",
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: float = 1.0
    ) -> None:
        """Generate PNG file from yaml_dict schema using Mermaid CLI.

        Args:
            output_path: Path where the PNG file will be saved
            direction: Diagram direction (TB, LR, RL, BT). Default is "TB"
            width: Optional width in pixels
            height: Optional height in pixels
            scale: Scale factor for the output image. Default is 1.0

        Raises:
            FileNotFoundError: If mermaid-cli (mmdc) is not installed

        Example:
            >>> sman = SMan(yaml_str)
            >>> sman.save_mermaid_png("schema.png")
            >>> sman.save_mermaid_png("schema.png", direction="LR", width=1200, scale=2.0)

        Note:
            Requires mermaid-cli to be installed:
            npm install -g @mermaid-js/mermaid-cli
        """
        # Get Mermaid code using the mermaid method
        mermaid_code = self.mermaid(direction=direction)

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

    def add_fks(self, spec_file_path: str) -> None:
        """Add foreign keys to tables according to specification from YAML file.

        Args:
            spec_file_path: Path to YAML file containing FK definitions
        Side effects:
            Modifies self.yaml_dict in place

        YAML file format:
            foreign_keys:
            - OrgUnit|Head|-->|Employee|EID
            - OrgUnit|SuperUnit|-->|OrgUnit|OEID

        Each line format: source_table|source_cols|-->|target_table|target_cols

        Example:
            >>> sman = RelSchemaMan(yaml_str)
            >>> sman.add_fks("path/to/fks.yaml")
        """
        # Read YAML file
        with open(spec_file_path, 'r') as f:
            fk_data = yaml.safe_load(f)

        # Extract foreign_keys list
        if not isinstance(fk_data, dict) or 'foreign_keys' not in fk_data:
            raise ValueError(f"YAML file must contain 'foreign_keys' key with list of FK specs")

        fk_specs = fk_data['foreign_keys']
        if not isinstance(fk_specs, list):
            raise ValueError(f"'foreign_keys' must be a list")

        # Process each FK spec
        for line in fk_specs:
            if not line or isinstance(line, str) and line.strip().startswith('#'):
                continue

            line = line.strip()

            # Check for |-->| separator
            if '|-->|' not in line:
                raise ValueError(f"Invalid FK spec line (missing '|-->|'): {line}")

            # Split by |-->|
            parts = line.split('|-->|')
            if len(parts) != 2:
                raise ValueError(f"Invalid FK spec line (multiple '|-->|'): {line}")

            source_part = parts[0].strip()
            target_part = parts[1].strip()

            # Parse source part: table | col1, col2, ...
            source_tokens = [t.strip() for t in source_part.split('|')]
            if len(source_tokens) != 2:
                raise ValueError(f"Invalid source spec (expected 'table | cols'): {source_part}")

            source_table = source_tokens[0]
            source_cols = [c.strip() for c in source_tokens[1].split(',')]

            # Parse target part: table | col1, col2, ...
            target_tokens = [t.strip() for t in target_part.split('|')]
            if len(target_tokens) != 2:
                raise ValueError(f"Invalid target spec (expected 'table | cols'): {target_part}")

            target_table = target_tokens[0]
            target_cols = [c.strip() for c in target_tokens[1].split(',')]

            # Validate column count match
            if len(source_cols) != len(target_cols):
                raise ValueError(
                    f"Column count mismatch: source has {len(source_cols)}, target has {len(target_cols)}"
                )

            # Generate FK name
            cols_suffix = '_'.join(source_cols)
            fk_name = f"fk_{source_table}_{target_table}_{cols_suffix}_1"

            # Find source table and add FK
            if 'tables' not in self.yaml_dict:
                raise ValueError("No tables found in schema")

            table_found = False
            for table in self.yaml_dict['tables']:
                if table.get('tablename') == source_table:
                    table_found = True

                    # Initialize foreign_keys if not present
                    if 'foreign_keys' not in table:
                        table['foreign_keys'] = []

                    # Create FK entry
                    fk_entry = {
                        'fkname': fk_name,
                        'sourcecolumns': source_cols,
                        'targettable': target_table,
                        'targetcolumns': target_cols
                    }

                    table['foreign_keys'].append(fk_entry)
                    break

            if not table_found:
                raise ValueError(f"Source table not found: {source_table}")

    def remove_tags(self, spec_file_path: str) -> None:
        """Remove specified tags (keys) from the YAML schema dictionary.

        Recursively traverses the data structure and removes any keys that match
        the tags in the omit_tags list.

        Args:
            spec_file_path: Path to YAML file containing tag names to omit

        Side effects:
            Modifies self.yaml_dict in place

        YAML file format:
            omit_tags:
            - nullable
            - fkname

        Example:
            >>> sman = RelSchemaMan(yaml_str)
            >>> sman.remove_tags("path/to/tags.yaml")
        """
        # Read YAML file
        with open(spec_file_path, 'r') as f:
            tags_data = yaml.safe_load(f)

        # Extract omit_tags list
        if not isinstance(tags_data, dict) or 'omit_tags' not in tags_data:
            raise ValueError(f"YAML file must contain 'omit_tags' key with list of tags")

        omit_tags = tags_data['omit_tags']
        if not isinstance(omit_tags, list):
            raise ValueError(f"'omit_tags' must be a list")

        self.yaml_dict = self._yaml_remove_tags_recursive(self.yaml_dict, omit_tags)

    def _yaml_remove_tags_recursive(self, data: Any, omit_tags: List[str]) -> Any:
        """Recursively remove tags from data structure.

        Args:
            data: Data structure to process (dict, list, or primitive)
            omit_tags: List of tag names (keys) to omit

        Returns:
            Data structure with specified tags removed
        """
        if isinstance(data, dict):
            return {
                key: self._yaml_remove_tags_recursive(value, omit_tags)
                for key, value in data.items()
                if key not in omit_tags
            }
        elif isinstance(data, list):
            return [self._yaml_remove_tags_recursive(item, omit_tags) for item in data]
        else:
            return data

    def _apply_transformation(self, schema: Dict[str, Any], spec_line: str) -> Dict[str, Any]:
        """Apply a single transformation step to schema."""

        # Parse the spec line
        match = re.match(r'del\s+table\s+pattern:(.+)', spec_line)
        if match:
            pattern = match.group(1).strip()
            return self._delete_tables_by_pattern(schema, pattern)

        match = re.match(r'del\s+table\s+index:(.+)', spec_line)
        if match:
            index_spec = match.group(1).strip()
            return self._delete_tables_by_index(schema, index_spec)

        match = re.match(r'del\s+column\s+(\S+)\s+pattern:(.+)', spec_line)
        if match:
            table = match.group(1).strip()
            pattern = match.group(2).strip()
            if table == '*':
                return self._delete_columns_all_tables_by_pattern(schema, pattern)
            else:
                return self._delete_columns_by_pattern(schema, table, pattern)

        match = re.match(r'del\s+column\s+(\S+)\s+index:(.+)', spec_line)
        if match:
            table = match.group(1).strip()
            index_spec = match.group(2).strip()
            return self._delete_columns_by_index(schema, table, index_spec)

        match = re.match(r'del\s+fk\s+pattern:(.+)', spec_line)
        if match:
            pattern = match.group(1).strip()
            return self._delete_fks_by_pattern(schema, pattern)

        match = re.match(r'del\s+fk\s+index:(.+)', spec_line)
        if match:
            index_spec = match.group(1).strip()
            return self._delete_fks_by_index(schema, index_spec)

        raise ValueError(f"Invalid spec line: {spec_line}")

    def _delete_tables_by_pattern(self, schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Delete tables matching pattern."""
        if 'tables' not in schema:
            return schema

        schema['tables'] = [
            table for table in schema['tables']
            if not fnmatch(table.get('tablename', ''), pattern)
        ]
        return schema

    def _delete_tables_by_index(self, schema: Dict[str, Any], index_spec: str) -> Dict[str, Any]:
        """Delete tables by index specification."""
        if 'tables' not in schema:
            return schema

        indexes = self._parse_index_spec(index_spec, len(schema['tables']))
        schema['tables'] = [
            table for i, table in enumerate(schema['tables'])
            if i not in indexes
        ]
        return schema

    def _delete_columns_by_pattern(self, schema: Dict[str, Any], tablename: str, pattern: str) -> Dict[str, Any]:
        """Delete columns matching pattern in specific table."""
        if 'tables' not in schema:
            return schema

        for table in schema['tables']:
            if table.get('tablename') == tablename and 'columns' in table:
                table['columns'] = [
                    col for col in table['columns']
                    if not fnmatch(col.get('columnname', ''), pattern)
                ]
        return schema

    def _delete_columns_by_index(self, schema: Dict[str, Any], tablename: str, index_spec: str) -> Dict[str, Any]:
        """Delete columns by index in specific table."""
        if 'tables' not in schema:
            return schema

        for table in schema['tables']:
            if table.get('tablename') == tablename and 'columns' in table:
                indexes = self._parse_index_spec(index_spec, len(table['columns']))
                table['columns'] = [
                    col for i, col in enumerate(table['columns'])
                    if i not in indexes
                ]
        return schema

    def _delete_columns_all_tables_by_pattern(self, schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Delete columns matching pattern across all tables."""
        if 'tables' not in schema:
            return schema

        for table in schema['tables']:
            if 'columns' in table:
                table['columns'] = [
                    col for col in table['columns']
                    if not fnmatch(col.get('columnname', ''), pattern)
                ]
        return schema

    def _delete_fks_by_pattern(self, schema: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        """Delete foreign keys matching pattern."""
        if 'tables' not in schema:
            return schema

        for table in schema['tables']:
            if 'foreign_keys' in table:
                table['foreign_keys'] = [
                    fk for fk in table['foreign_keys']
                    if not fnmatch(fk.get('fkname', ''), pattern)
                ]
        return schema

    def _delete_fks_by_index(self, schema: Dict[str, Any], index_spec: str) -> Dict[str, Any]:
        """Delete foreign keys by index across all tables."""
        if 'tables' not in schema:
            return schema

        for table in schema['tables']:
            if 'foreign_keys' in table:
                indexes = self._parse_index_spec(index_spec, len(table['foreign_keys']))
                table['foreign_keys'] = [
                    fk for i, fk in enumerate(table['foreign_keys'])
                    if i not in indexes
                ]
        return schema

    def _parse_index_spec(self, spec: str, length: int) -> set:
        """Parse index specification into set of indexes.

        Supports:
            0           - Single index
            [0,2,4]     - List of indexes
            [1:5]       - Slice
            [::2]       - Slice with step
            [1:3,5:7]   - Multiple slices/indexes
        """
        indexes = set()

        # Single index (no brackets)
        if not spec.startswith('['):
            indexes.add(int(spec))
            return indexes

        # Remove brackets
        spec = spec[1:-1]

        # Split by comma
        parts = spec.split(',')

        for part in parts:
            part = part.strip()

            # Slice notation
            if ':' in part:
                # Parse slice
                slice_parts = part.split(':')
                start = int(slice_parts[0]) if slice_parts[0] else None
                stop = int(slice_parts[1]) if len(slice_parts) > 1 and slice_parts[1] else None
                step = int(slice_parts[2]) if len(slice_parts) > 2 and slice_parts[2] else None

                # Convert slice to indexes
                slice_obj = slice(start, stop, step)
                indexes.update(range(*slice_obj.indices(length)))
            else:
                # Single index
                indexes.add(int(part))

        return indexes

