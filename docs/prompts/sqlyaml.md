### create a python util function that transpiles SQL into yaml
- use sqlglot library
- the function has the following parameters
  - path of SQL file
  - SQL dialect
  - path of yaml file
- the yaml file should have following structure
  ```yaml
  tables:
  - name: users
    columns:
    - name: id
      type: INTEGER
      constraints: "NOT NULL"
    - name: username
      type: VARCHAR(50)
      constraints: "NOT NULL"
    - name: email
      type: VARCHAR(100)
      constraints: "NOT NULL"
    primary_key:
    - id
  - name: orders
    columns:
    - name: id
      type: INTEGER
    - name: user_id
      type: INTEGER
      constraints: "NOT NULL"
    - name: user_email
      type: VARCHAR(100)
      constraints: "NOT NULL"
    - name: order_date
      type: DATETIME
      constraints: "NOT NULL"
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
- take also ALTER TABLE for foreign key constraints into account
