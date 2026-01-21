"""Tests for yaml transformation utilities."""

import pytest
import yaml
from edurel.utils.yaml_utils import yaml_to_yaml, _parse_index_spec


# Sample schema for testing
SAMPLE_SCHEMA = """tables:
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
  - columnname: attribute2
    type: DATE
    nullable: False
  - columnname: attribute3
    type: DECIMAL(9,2)
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
- tablename: table3
  columns:
  - columnname: id3
    type: INTEGER
    nullable: False
  - columnname: name
    type: TEXT
    nullable: True
  primary_key:
  - id3
"""


def test_delete_table_by_pattern():
    """Test deleting tables by pattern."""
    spec = "del table pattern:table2"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 2
    assert schema['tables'][0]['tablename'] == 'table1'
    assert schema['tables'][1]['tablename'] == 'table3'


def test_delete_table_by_pattern_wildcard():
    """Test deleting tables by pattern with wildcard."""
    spec = "del table pattern:table*"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 0


def test_delete_table_by_index_single():
    """Test deleting table by single index."""
    spec = "del table index:1"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 2
    assert schema['tables'][0]['tablename'] == 'table1'
    assert schema['tables'][1]['tablename'] == 'table3'


def test_delete_table_by_index_list():
    """Test deleting tables by list of indexes."""
    spec = "del table index:[0,2]"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 1
    assert schema['tables'][0]['tablename'] == 'table2'


def test_delete_table_by_index_slice():
    """Test deleting tables by slice."""
    spec = "del table index:[1:3]"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 1
    assert schema['tables'][0]['tablename'] == 'table1'


def test_delete_column_by_pattern():
    """Test deleting columns by pattern in specific table."""
    spec = "del column table2 pattern:attribute*"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    table2 = next(t for t in schema['tables'] if t['tablename'] == 'table2')
    column_names = [c['columnname'] for c in table2['columns']]

    assert 'id2' in column_names
    assert 'fk1' in column_names
    assert 'attribute2' not in column_names
    assert 'attribute3' not in column_names


def test_delete_column_by_index():
    """Test deleting columns by index in specific table."""
    spec = "del column table2 index:[2,3]"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    table2 = next(t for t in schema['tables'] if t['tablename'] == 'table2')
    column_names = [c['columnname'] for c in table2['columns']]

    assert len(column_names) == 2
    assert column_names == ['id2', 'fk1']


def test_delete_column_all_tables_by_pattern():
    """Test deleting columns by pattern across all tables."""
    spec = "del column * pattern:id*"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    for table in schema['tables']:
        column_names = [c['columnname'] for c in table['columns']]
        assert not any(name.startswith('id') for name in column_names)


def test_delete_fk_by_pattern():
    """Test deleting foreign keys by pattern."""
    spec = "del fk pattern:fk_table2*"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    table2 = next(t for t in schema['tables'] if t['tablename'] == 'table2')
    assert 'foreign_keys' not in table2 or len(table2['foreign_keys']) == 0


def test_delete_fk_by_index():
    """Test deleting foreign keys by index."""
    spec = "del fk index:0"
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    table2 = next(t for t in schema['tables'] if t['tablename'] == 'table2')
    assert 'foreign_keys' not in table2 or len(table2['foreign_keys']) == 0


def test_multiple_transformations():
    """Test applying multiple transformations."""
    spec = """
    del table pattern:table3
    del column table2 pattern:attribute*
    del fk pattern:*
    """
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)

    assert len(schema['tables']) == 2

    table2 = next(t for t in schema['tables'] if t['tablename'] == 'table2')
    column_names = [c['columnname'] for c in table2['columns']]
    assert 'attribute2' not in column_names
    assert 'attribute3' not in column_names
    assert 'foreign_keys' not in table2 or len(table2['foreign_keys']) == 0


def test_parse_index_spec_single():
    """Test parsing single index."""
    indexes = _parse_index_spec("2", 10)
    assert indexes == {2}


def test_parse_index_spec_list():
    """Test parsing list of indexes."""
    indexes = _parse_index_spec("[0,2,4]", 10)
    assert indexes == {0, 2, 4}


def test_parse_index_spec_slice():
    """Test parsing slice."""
    indexes = _parse_index_spec("[1:4]", 10)
    assert indexes == {1, 2, 3}


def test_parse_index_spec_slice_with_step():
    """Test parsing slice with step."""
    indexes = _parse_index_spec("[0:6:2]", 10)
    assert indexes == {0, 2, 4}


def test_parse_index_spec_open_slice():
    """Test parsing open-ended slice."""
    indexes = _parse_index_spec("[::2]", 10)
    assert indexes == {0, 2, 4, 6, 8}


def test_parse_index_spec_multiple():
    """Test parsing multiple slices and indexes."""
    indexes = _parse_index_spec("[0,2:5,7]", 10)
    assert indexes == {0, 2, 3, 4, 7}


def test_empty_spec():
    """Test that empty spec returns original schema."""
    result = yaml_to_yaml(SAMPLE_SCHEMA, "")
    schema = yaml.safe_load(result)
    assert len(schema['tables']) == 3


def test_comment_lines_ignored():
    """Test that comment lines are ignored."""
    spec = """
    # This is a comment
    del table pattern:table3
    # Another comment
    """
    result = yaml_to_yaml(SAMPLE_SCHEMA, spec)
    schema = yaml.safe_load(result)
    assert len(schema['tables']) == 2


def test_invalid_spec_line():
    """Test that invalid spec line raises ValueError."""
    spec = "invalid command"
    with pytest.raises(ValueError, match="Invalid spec line"):
        yaml_to_yaml(SAMPLE_SCHEMA, spec)
