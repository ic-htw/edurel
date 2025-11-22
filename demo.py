from pathlib import Path
from edurel.sql_to_yaml import sql_to_yaml

SQL_DIR = "/home/basis/work/github/edurel/data/sql"
sql_file = "t1.sql"
sql_path_obj = Path(SQL_DIR) / sql_file

if not sql_path_obj.exists():
   raise FileNotFoundError(f"SQL file not found: {str(sql_path_obj)}")

sql_content = sql_path_obj.read_text(encoding='utf-8')

print(sql_content)

# ast = sqlglot.parse(sql_content, dialect="postgres")
# print(repr(ast))

y = sql_to_yaml(str(sql_path_obj))
print(y)