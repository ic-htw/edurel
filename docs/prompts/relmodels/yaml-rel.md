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
  - columnname: attribute2
    type: DATE
    nullable: False
  - columnname: attribute3
    type: DECIMAL
    nullable: False
  primary_key:
  - id2
  foreign_keys:
  - name: fk_table2_table1
    sourcecolumns:
    - fk1
    targettable: table1
    targetcolumns:
    - id1
```
