# write a python function that transforms yaml input into yaml output
- the name of the function should be yaml_to_yaml
- put the code in yaml.py in utils folder
- the yaml input contains the schema of a relational database, as follows
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
  ```
## parameters
- yaml - a string containg the yaml input
- spec - a string containing a specification describing the transformation
## result
- a string containg the yaml output
## instructions
- the spec should be able to express the following transformation steps
  - pattern-based deletion of complete tables
  - index-based deletion of complete tables
  - pattern-based deletion of columns within tables
  - index-based deletion of columns within tables
  - pattern-based deletion of columns over all tables
  - pattern-based deletion of foreign keys
  - index-based deletion of foreign keys

- indexes should be positions within yaml list elements
- all index-based steps should allow for single indexes, list of indexes, slices, list of slices
- the spec should be very compact with each step on a single line
