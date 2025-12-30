# write a python function that transforms yaml to mermaid
- put the code in misc.py in utils folder
- the yaml file contains the schema of a relational database, as follows
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
- a dictionary correponding to the yaml file
## result
- mermaid code for an er diagram
## instructions
- the yaml might contain type information with a sizes indicator in brackets
- remove these indicators in the mermaid output
