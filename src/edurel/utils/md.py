import re
from IPython.display import display, Markdown

# ---------------------------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------------------------
def md_sql(str):
    return f"```sql\n{str}\n```"

def md_yaml(str):
    return f"```yaml\n{str}\n```"

def md_plain(str):
    return f"```plaintext\n{str}\n```"

def display_md(str):  
    display(Markdown(str))

def display_sql(str):  
    display(Markdown(md_sql(str)))

def display_yaml(str):  
    display(Markdown(md_yaml(str)))

def sql_extract(md):
    # First, try to extract from markdown code blocks
    # Look for ```sql ... ``` blocks
    sql_block_pattern = r'```sql\s*\n(.*?)\n```'
    matches = re.findall(sql_block_pattern, md, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Look for generic ``` ... ``` blocks that might contain SQL
    generic_block_pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(generic_block_pattern, md, re.DOTALL)
    for match in matches:
        # Check if it looks like SQL (starts with common SQL keywords)
        if re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b',
                   match, re.IGNORECASE):
            return match.strip()

    # If no markdown blocks, try to extract SQL from plain text
    # Look for SQL statements (starting with common keywords at line start)
    sql_pattern = r'(?:^|\n)\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b.*?)(?=\n\n|\Z)'
    matches = re.findall(sql_pattern, md, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if matches:
        return matches[0].strip()

    return ""

def yaml_extract(md):
    # First, try to extract from ```yaml ... ``` blocks
    yaml_block_pattern = r'```yaml\s*\n(.*?)\n```'
    matches = re.findall(yaml_block_pattern, md, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Also try ```yml ... ``` blocks
    yml_block_pattern = r'```yml\s*\n(.*?)\n```'
    matches = re.findall(yml_block_pattern, md, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Look for generic ``` ... ``` blocks that might contain YAML
    generic_block_pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(generic_block_pattern, md, re.DOTALL)
    if matches:
        # Return the first generic block (assume it's YAML if no language specified)
        return matches[0].strip()

    return ""

