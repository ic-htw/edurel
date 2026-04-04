from IPython.display import display, Markdown

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