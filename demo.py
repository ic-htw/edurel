from pathlib import Path
import sqlglot
from edurel.sql_to_yaml import sql_to_yaml


BASE_DIR = "/home/basis/work/github/edurel"
DB_DIR = f"{BASE_DIR}/databases/"

sql_path_obj = Path(DB_DIR) / "db-hvs/schema1.sql"

if not sql_path_obj.exists():
   raise FileNotFoundError(f"SQL file not found: {str(sql_path_obj)}")

sql_content = sql_path_obj.read_text(encoding='utf-8')

# print(sql_content)

# ast = sqlglot.parse(sql_content, dialect="postgres")
# print(repr(ast))

y = sql_to_yaml(str(sql_path_obj))
print(y)