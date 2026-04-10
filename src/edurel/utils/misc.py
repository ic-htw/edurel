from pathlib import Path
from urllib.request import urlopen

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

def save_text_to_file(text: str, output_path: str, overwrite: bool = False) -> None:
    file_path = Path(output_path)
    if not overwrite and file_path.exists():
        display_md(md_plain(f"File {output_path} already exists. Use overwrite=True to overwrite."))
        return
    file_path.write_text(text)
    display_md(md_plain(f"Text saved to {output_path}"))

def save_from_url(file: str, url: str, dir: str, overwrite: bool = False) -> None:
    dir_path = Path(dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / file
    if not overwrite and file_path.exists():
        display_md(md_plain(f"File {file_path} already exists. Use overwrite=True to overwrite."))
        return

    with urlopen(url) as response:
        file_path.write_bytes(response.read())

    display_md(md_plain(f"Downloaded {url} to {file_path}"))
