### create a function schema_yaml(con)
- returns database schema as a dictionary suitable for YAML serialization
- the function has the following parameters
  - con: connection to duckdb database
- the yaml dump from the dictionary should have following structure
  ```yaml
  tables:
  - name: users
    columns:
    - name: id
      type: INTEGER
      nullable: True/False
    - name: username
      type: TEXT
      nullable: True/False
    - name: email
      type: TEXT
      nullable: True/False
    primary_key:
    - id
  - name: orders
    columns:
    - name: id
      type: INTEGER
      nullable: True/False
    - name: user_id
      type: INTEGER
      nullable: True/False
    - name: user_email
      type: VARCHAR(100)
      nullable: True/False
    - name: order_date
      type: DATETIME
      nullable: True/False
    - name: total
      type: DECIMAL(10,2)
    primary_key:
    - id
    foreign_keys:
    - name: fk_users_user_id
      columns:
      - user_id
      ref_table: users
      ref_columns:
      - id
  ```
- compound primary keys should be possible
- compound foreign keys should be possible
