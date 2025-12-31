# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**edurel** is a Python library for education tools related to relational data. It provides utilities for working with DuckDB and SQLite databases, generating schema visualizations, managing data collections, and integrating with LLM providers for educational purposes.

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
pytest tests/test_sql_to_yaml.py

# Run specific test function
pytest tests/test_sql_to_yaml.py::test_<function_name>
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
    - `duckdb.py`: DuckDB connection and metadata utilities (primary database interface)
    - `sqlite.py`: SQLite connection and metadata utilities
    - `sql_to_yaml.py`: SQL-to-YAML transpiler
    - `mermaid.py`: Schema-to-Mermaid ER diagram conversion
    - `llm.py`: LangChain-based LLM client factories (OpenAI, Anthropic, Ollama, custom endpoints)
    - `misc.py`: Miscellaneous utilities
  - `widgets/`: Interactive Jupyter notebook widgets
    - `listman.py`: ListManager widget for managing lists with filtering, sorting, and JSON persistence
    - `schema_viz.py`: SchemaVisualizer widget for visualizing database schemas from YAML
    - `mermaid_viz.py`: MermaidVisualizer widget for rendering Mermaid diagrams
- `tests/`: Test suite
- `databases/`: Example database directories (each contains schema.sql, data.sql, mermaid.txt)
- `experiments/`: Jupyter notebooks for experimentation (sql-*.ipynb patterns)
- `docs/`: Documentation and design specs
  - `architecture/`: Architecture documentation and API specs
  - `prompts/`: Development prompts and specifications
  - `spider2/`: Spider2 benchmark databases
- `data/`: Data files (JSON, YAML, etc.)

### Key Dependencies
- **duckdb** (>=1.4): Primary database engine
- **sqlglot** (>=28.0): SQL parsing and transpilation
- **pyyaml** (>=6.0): YAML processing
- **pandas**: Data manipulation
- **ipywidgets** (>=8.0): Jupyter notebook widgets
- **langchain-core, langchain-openai, langchain-anthropic, langchain-ollama**: LLM integrations
- **openai, anthropic, google-genai**: Direct API clients
- **python-dotenv**: Environment variable management
- Python 3.12+

### Database Directory Structure
Each database in `databases/` follows this pattern:
```
databases/<db_name>/
├── schema.sql      # DDL statements (CREATE TABLE, constraints)
├── data.sql        # DML statements (INSERT data) [optional]
└── mermaid.txt     # Mermaid ER diagram representation [optional]
```

Load databases using `mem_con1()` which reads schema.sql and data.sql files.

### DuckDB Utilities (`src/edurel/utils/duckdb.py`)
Primary interface for database operations. Key functions:

#### Connection Management
- `con_mem()`: Create empty in-memory DuckDB connection
- `mem_con1(db_path, verbose=False)`: Create in-memory connection and load schema.sql/data.sql from directory
- `con_file(db_file_path, read_only=True)`: Connect to DuckDB file
- `exe_sql_file(con, sql_file_path)`: Execute SQL file against connection

#### Metadata Extraction (per-table)
- `tablenames(con)`: Get list of all table names
- `columns(con, tablename)`: Get column info for table (columnname, type, nullable)
- `primary_keys(con, tablename)`: Get primary key columns for table
- `foreign_keys(con, tablename)`: Get foreign key relationships for table
- `to_fk_dict(fk_str)`: Convert FK string to standardized dict format

#### Schema Operations
- `schema_yaml(con, additional_fks)`: Convert entire database schema to YAML dict structure
- `schema(con)`: Get schema as formatted string
- `schema_yaml_print(con, additional_fks)`: Print schema as YAML
- `schema_print(con)`: Print schema as formatted text

#### Query and Display
- `sql_print(con, sql)`: Execute and print query results
- `sql_df(con, sql)`: Execute query and return pandas DataFrame
- `data_print(con, spec)`: Print table data with optional filtering (spec: {table: "WHERE clause"})
- `df_print(con, spec)`: Print table data as DataFrame with optional filtering
- `tablenames_print(con)`: Print list of table names

#### Data Conversion
- `csv_to_parquet(...)`: Convert CSV to Parquet format

### SQLite Utilities (`src/edurel/utils/sqlite.py`)
Similar interface to duckdb.py but for SQLite databases:
- `file_con(db_path)`: Connect to SQLite file
- `sql_print(con, sql)`, `sql_df(con, sql)`: Query utilities
- `tablenames(con)`, `columns(con, tablename)`: Metadata extraction
- `schema_yaml(con)`, `schema_print(con)`, `schema_yaml_print(con)`: Schema operations

### YAML Schema Format
The project uses a standardized YAML format for relational schemas (see `docs/architecture/yaml-rel.md`):
```yaml
tables:
- tablename: table1
  columns:
  - columnname: id1
    type: INTEGER
    nullable: False
  - columnname: attribute1
    type: TEXT
    nullable: True
  primary_key:
  - id1
- tablename: table2
  columns:
  - columnname: id2
    type: INTEGER
    nullable: False
  - columnname: fk1
    type: INTEGER
    nullable: False
  primary_key:
  - id2
  foreign_keys:
  - fkname: fk_table2_table1_1
    sourcecolumns:
    - fk1
    targettable: table1
    targetcolumns:
    - id1
```

### Mermaid Utilities (`src/edurel/utils/mermaid.py`)
- `schema_to_mermaid(schema)`: Convert YAML schema dict to Mermaid ER diagram syntax

### LLM Utilities (`src/edurel/utils/llm.py`)
Factory functions for creating LangChain chat clients:
- `openai_c(model, timeout=60, max_retries=0, temperature=0)`: OpenAI client
- `anthropic_c(model, timeout=60, max_retries=0, temperature=0)`: Anthropic client
- `ollama_c(model, timeout=60, max_retries=0, temperature=0)`: Ollama client (uses OLLAMA_API_URL from .env)
- `stats_c(model, timeout=60, max_retries=0, temperature=0)`: Custom stats API client (uses LLM_STATS_API_KEY from .env)

All functions return LangChain chat clients configured with the specified parameters.

### Jupyter Widgets

#### ListManager (`src/edurel/widgets/listman.py`)
Reusable component for managing lists in notebooks:
- Interactive list management with add/edit/delete operations
- Real-time search/filtering
- Sorting (ascending, descending, original order)
- Selection tracking via checkboxes
- JSON persistence (auto-save/load)
- File upload/download with merge support

Usage:
```python
from edurel.widgets import ListManager
manager = ListManager(filename="my_list.json", directory="./data")
manager.display()
selected = manager.get_selected_items()
```

#### SchemaVisualizer (`src/edurel/widgets/schema_viz.py`)
Widget for visualizing database schemas:
- Load YAML schema files via file selector
- Convert schema to Mermaid ER diagram syntax
- Display diagram code in text output pane
- Render interactive visual diagram using Mermaid.js
- Supports tables, columns, primary keys, and foreign keys

Usage:
```python
from edurel.widgets import SchemaVisualizer
viz = SchemaVisualizer(directory="./data")
viz.display()
# Or load programmatically:
viz.load_from_path("./data/example_schema.yaml")
```

#### MermaidVisualizer (`src/edurel/widgets/mermaid_viz.py`)
General-purpose widget for rendering Mermaid diagrams from code:
- Accepts Mermaid diagram code as input
- Renders interactive diagrams using Mermaid.js
- Configurable width and height
- Includes text input pane and visualize button

Usage:
```python
from edurel.widgets import MermaidVisualizer
viz = MermaidVisualizer(initial_code="graph TD; A-->B;", width="100%", height="500px")
viz.display()
```

#### MermaidViz (`src/edurel/widgets/mermaid_viz.py`)
Simplified widget for programmatic Mermaid diagram rendering:
- Only displays rendered diagram (no text input or button)
- Automatically redraws when code is set via `set_code()`
- Configurable width and height
- Ideal for programmatic diagram generation

Usage:
```python
from edurel.widgets import MermaidViz
viz = MermaidViz(initial_code="graph TD; A-->B;", width="100%", height="500px")
viz.display()
# Update diagram programmatically
viz.set_code("graph LR; X-->Y;")
```

## Code Style
- Line length: 88 characters (Black default)
- Target Python version: 3.8+ (for compatibility)
- Use type hints where helpful
- Follow pytest naming conventions: `test_*.py`, `Test*` classes, `test_*` functions

## Environment Variables
The project uses `.env` file for configuration (ignored by git). Required variables:
- `OLLAMA_API_URL`: Base URL for Ollama API (for `ollama_c()`)
- `LLM_STATS_API_KEY`: API key for custom stats endpoint (for `stats_c()`)
- Standard LLM API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.
