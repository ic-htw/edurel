import re

def sql_extract(text):
    """Extract SQL code from text (supports both plain text and markdown).

    Args:
        text: A string with embedded SQL statement(s)

    Returns:
        str: Extracted SQL code, or empty string if no SQL found
    """
    # First, try to extract from markdown code blocks
    # Look for ```sql ... ``` blocks
    sql_block_pattern = r'```sql\s*\n(.*?)\n```'
    matches = re.findall(sql_block_pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0].strip()

    # Look for generic ``` ... ``` blocks that might contain SQL
    generic_block_pattern = r'```\s*\n(.*?)\n```'
    matches = re.findall(generic_block_pattern, text, re.DOTALL)
    for match in matches:
        # Check if it looks like SQL (starts with common SQL keywords)
        if re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b',
                   match, re.IGNORECASE):
            return match.strip()

    # If no markdown blocks, try to extract SQL from plain text
    # Look for SQL statements (starting with common keywords at line start)
    sql_pattern = r'(?:^|\n)\s*((?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH)\b.*?)(?=\n\n|\Z)'
    matches = re.findall(sql_pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if matches:
        return matches[0].strip()

    return ""


