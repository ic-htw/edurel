# extend method show_conversation
- add a new optional parameter lastn_only
- if lastn_only is not given, show complete conversion historey
- if lastn_only is given show only the last n entries

# Enhance the code structure of duck_utils
- think about useful refactorings
- add type hints
- add function docs

# update claude.md 
- add the following functions from xxx: 
  - xxx, 
  - xxx
- update package structure in claude.md 

# db
- add a class factory method mem to class Db with no parameters
- add a class factory method file to class Db 
- paramter 1: db_file_path
- optional paramter 2: read_only, default True

# Refactor
- refactor dbcon.py by using class Db from db.py
- refactor function csv_to_parquet of duckdbalt.py using class Db from db.py and copy the result into misc.py

# Db
- turn the following functions of duckdbalt.py into methods of class Db in db.py
  - tablenames
  - columns
  - primary_keys
  - foreign_keys
- use instance variable self.con

# Db YAML
- add method yaml to class Db in db.py
- it should use methods tablenames, columns, primary_keys, foreign_keys
- it should return yaml string conforming to the structure given in the following example
tables:
- tablename: EmpProj
  columns:
  - columnname: EID
    type: INTEGER
    nullable: false
  - columnname: PID
    type: INTEGER
    nullable: false
  - columnname: NoOfHoursPerWeek
    type: INTEGER
    nullable: false
  primary_key:
  - EID
  - PID
  foreign_keys:
  - fkname: fk_EmpProj_Employee_EID_1
    sourcecolumns:
    - EID
    targettable: Employee
    targetcolumns:
    - EID
  - fkname: fk_EmpProj_Project_PID_1
    sourcecolumns:
    - PID
    targettable: Project
    targetcolumns:
    - PID
- tablename: Employee
  columns:
  - columnname: EID
    type: INTEGER
    nullable: false
  - columnname: OUID
    type: INTEGER
    nullable: false
  - columnname: LastName
    type: VARCHAR
    nullable: false
  - columnname: Hiredate
    type: DATE
    nullable: false
  - columnname: Salary
    type: DECIMAL(9,2)
    nullable: false
  - columnname: Bonus
    type: DECIMAL(9,2)
    nullable: true
  primary_key:
  - EID
  foreign_keys:
  - fkname: fk_Employee_OrgUnit_OUID_1
    sourcecolumns:
    - OUID
    targettable: OrgUnit
    targetcolumns:
    - OUID
- tablename: OrgUnit
  columns:
  - columnname: OUID
    type: INTEGER
    nullable: false
  - columnname: Head
    type: INTEGER
    nullable: true
  - columnname: SuperUnit
    type: INTEGER
    nullable: true
  - columnname: Name
    type: VARCHAR
    nullable: false
  primary_key:
  - OUID
- tablename: Project
  columns:
  - columnname: PID
    type: INTEGER
    nullable: false
  - columnname: Title
    type: VARCHAR
    nullable: false
  - columnname: Budget
    type: DECIMAL(13,2)
    nullable: true
  primary_key:
  - PID