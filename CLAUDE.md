# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**edurel** is a Python library for education tools related to relational data.

## Development Commands

### Setup
```bash
# Install package in editable mode with dev and notebook dependencies
pip install -e ".[dev,notebook]"
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=edurel

# Run specific test file
pytest tests/test_<module>.py

# Run specific test function
pytest tests/test_<module>.py::test_<function_name>
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Fix auto-fixable linting issues
ruff check --fix src/ tests/
```

## Architecture

### Package Structure
- `src/edurel/`: Main package code
  - `utils/`: Utility modules
    - `duck_utils.py`: DuckDB connection and metadata utilities
    - `sql_to_yaml.py`: SQL-to-YAML transpiler
  - `widgets/`: Interactive Jupyter notebook widgets
    - `listman.py`: ListManager widget for managing lists with filtering, sorting, and JSON persistence
    - `schema_viz.py`: SchemaVisualizer widget for visualizing database schemas from YAML
- `tests/`: Test suite
- `notebooks/`: Jupyter notebooks for experimentation and examples
- `docs/prompts/`: Development prompts and specifications
- `data/`: Data files (JSON, YAML, etc.)

### Key Dependencies
- **sqlglot** (>=28.0): SQL parsing and transpilation
- **pyyaml** (>=6.0): YAML processing
- **ipywidgets** (>=8.0): Jupyter notebook widgets
- Python 3.12+

### ListManager Widget
The `ListManager` class (`src/edurel/widgets/listman.py`) is a reusable Jupyter notebook component that provides:
- Interactive list management with add/edit/delete operations
- Real-time search/filtering
- Sorting (ascending, descending, original order)
- Selection tracking via checkboxes
- JSON persistence (auto-save/load)
- File upload/download with merge support

Usage pattern:
```python
from edurel.widgets import ListManager
manager = ListManager(filename="my_list.json", directory="./data")
manager.display()
selected = manager.get_selected_items()
```

### SchemaVisualizer Widget
The `SchemaVisualizer` class (`src/edurel/widgets/schema_viz.py`) is a Jupyter notebook widget for visualizing database schemas:
- Load YAML schema files via file selector
- Convert schema to Mermaid ER diagram syntax
- Display diagram code in text output pane
- Render interactive visual diagram using Mermaid.js
- Supports tables, columns, primary keys, and foreign keys

Usage pattern:
```python
from edurel.widgets import SchemaVisualizer
viz = SchemaVisualizer(directory="./data")
viz.display()
# Or load programmatically:
viz.load_from_path("./data/example_schema.yaml")
```

### Database Metadata Utilities
The `duck_utils` module (`src/edurel/utils/duck_utils.py`) provides utilities for extracting database metadata from DuckDB connections:

#### `tablenames(con)`
Returns a list of all table names in the database.
```python
from edurel.utils.duck_utils import tablenames
tables = tablenames(con)  # ['customers', 'orders', 'products']
```

#### `columns(con)`
Returns a dictionary mapping table names to their column definitions. Each column includes name, type, and nullable status.
```python
from edurel.utils.duck_utils import columns
cols = columns(con)
# {
#   'customers': [
#     {'col': 'id', 'type': 'INTEGER', 'nullable': False},
#     {'col': 'name', 'type': 'VARCHAR', 'nullable': True}
#   ]
# }
```

#### `primary_keys(con)`
Returns a dictionary mapping table names to lists of primary key column names.
```python
from edurel.utils.duck_utils import primary_keys
pks = primary_keys(con)
# {'customers': ['id'], 'order_items': ['order_id', 'item_id']}
```

#### `foreign_keys(con)`
Returns a dictionary mapping source table names to their foreign key relationships. Each relationship includes the target table and column mappings.
```python
from edurel.utils.duck_utils import foreign_keys
fks = foreign_keys(con)
# {
#   'orders': [
#     {'customers': [['customer_id'], ['id']]}
#   ]
# }
```

## Code Style
- Line length: 88 characters (Black default)
- Target Python version: 3.8+ (for compatibility)
- Use type hints where helpful
- Follow pytest naming conventions: `test_*.py`, `Test*` classes, `test_*` functions
