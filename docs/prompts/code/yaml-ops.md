# write a python function that transforms a yaml file by reducing tags
- put the code in misc.py in utils folder
## parameters
- a dictionary correponding to the initial yaml file
- a list of tags that should be ommitted
## result
- a dictionary corresponding to the resulting yaml file

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


# write a python function that transforms er diagrams given in yaml into mermaid
- put the code in misc.py in utils folder
- the yaml file contains the schema of an er diagram, as follows
  ```yaml
entities:
# only atomic keys and attributes
# use associative_entities if composite keys are needed
- entityname: E1
  key: K1 
  attributes:
  - attributename: A11
    type: INTEGER
  - attributename: A12
    type: TEXT
  - attributename: A13
    type: DATE
  - attributename: A14
    type: DECIMAL
- entityname: E2
  key: K2
  attributes:
  - attributename: A21
    type: INTEGER
  - attributename: A22
    type: TEXT
  - attributename: A23
    type: DATE
  - attributename: A24
    type: DECIMAL

associative_entities:
# identification alternatives
# 1. just atomic key
# 2. identified by other entities (only with cardinality ONE)
# 3. combination of both
# if roles are omitted in associations, default roles are used (E1, E2, ...)
# Associations are entities and relationships at the same time
- associationname: AE1
  associations:
  - targetentity: E1
    role: Role1
    cardinality: ONE
  - targetentity: E2
    role: Role2 
    cardinality: ONE
  - targetentity: E3
    role: Role2 
    cardinality: MANY
  key: KAE1 #
  identified_by:
  - targetentity: E1
    cardinality: ONE
  - targetentity: E2
    cardinality: ONE
  attributes:
  - attributename: AEA1
    type: INTEGER
  - attributename: AEA2
    type: TEXT
  - attributename: AEA3
    type: DATE
  - attributename: AEA4
    type: DECIMAL

relationships:
# if roles are omitted in associations, default roles are used (E1, E2, ...)
# all relationships are binary
# cardinality values: ONE, MANY, OPTIONAL_ONE, OPTIONAL_MANY
- relationshipname: R1
  entities:
  - entityname: E1
    role: Role1
  - entityname: E2
    role: Role2
  cardinality:
    Role1: MANY
    Role2: ONE
  attributes:
  - attributename: RA1
    type: INTEGER
  - attributename: RA2
    type: TEXT
  - attributename: RA3
    type: DATE
  - attributename: RA4
    type: DECIMAL    

inheritances:
# only single inheritance is supported
- superentity: E1
  subentities:
  - E1A
  - E1B

valuelists:
# each valuelist is an entity with the following attributes:
# ID: INTEGER
# Description: TEXT
# IsValid: BOOLEAN
# SortOrder: INTEGER
# valulists will be transformed into tables in the relational schema
# each row in that table represents one value in the valuelist
- valuelistname: VL1
- valuelistname: VL2
  ```


## parameters
- a dictionary correponding to the yaml file
## result
- mermaid code for an er diagram
## instructions
- the yaml might contain type information with a sizes indicator in brackets
- remove these indicators in the mermaid output

