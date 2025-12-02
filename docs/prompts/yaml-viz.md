### create a jupyter notebook widget
- that has a file selector to read in a yaml file with the following structure
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
- this yaml file represents a relational data model
- the widget should have an text output pane1 and a button1
- clicking button1 the yaml should be turned into a graphical langage representaion and put in the text output pane
- the widget should have a graphical output pane1 and a button1
- clicking button2 the graphical langage representaion should be visualized in the output pane2
