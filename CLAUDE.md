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
  - `widgets/`: Interactive Jupyter notebook widgets
    - `listman.py`: ListManager widget for managing lists with filtering, sorting, and JSON persistence
- `tests/`: Test suite
- `notebooks/`: Jupyter notebooks for experimentation and examples
- `docs/prompts/`: Development prompts and specifications (e.g., SQL-to-YAML transpiler spec)
- `data/`: Data files (JSON, etc.)

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
from edurel.widgets.listman import ListManager
manager = ListManager(filename="my_list.json", directory="./data")
manager.display()
selected = manager.get_selected_items()
```

## Code Style
- Line length: 88 characters (Black default)
- Target Python version: 3.8+ (for compatibility)
- Use type hints where helpful
- Follow pytest naming conventions: `test_*.py`, `Test*` classes, `test_*` functions
