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

# generalized slices
- write a function gslice that provides generalized slicing of lists
- parameter: spec, string of form "i1, i2:i3, i4, i5:i6", i1-i6 are integers
- it should return a function that given a list returns a sub list containing only elements of the spec
- generate tests
- put gslice in misc.py in utils