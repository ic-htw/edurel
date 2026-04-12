from pathlib import Path
from typing import Callable, List, Any
from urllib.request import urlopen

# ---------------------------------------------------------------------------------------------
# File
# ---------------------------------------------------------------------------------------------
def save_text_to_file(text: str, output_path: str, overwrite: bool = False) -> None:
    file_path = Path(output_path)
    if not overwrite and file_path.exists():
        print(f"File {output_path} already exists. Use overwrite=True to overwrite.")
        return
    file_path.write_text(text)
    print(f"Text saved to {output_path}")

def save_from_url(file: str, url: str, dir: str, overwrite: bool = False) -> None:
    dir_path = Path(dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = dir_path / file
    if not overwrite and file_path.exists():
        print(f"File {file_path} already exists. Use overwrite=True to overwrite.")
        return

    with urlopen(url) as response:
        file_path.write_bytes(response.read())

    print(f"Downloaded {url} to {file_path}")

# ---------------------------------------------------------------------------------------------
# gslice
# ---------------------------------------------------------------------------------------------
def gslice(spec: str) -> Callable[[List[Any]], List[Any]]:
    """Create a generalized slicing function from a spec string.

    Args:
        spec: String of form "i1, i2:i3, i4, i5:i6" where indices are integers.
              Individual indices (i1, i4) select single elements.
              Range slices (i2:i3, i5:i6) select ranges [start:end) like Python slicing.
              Negative indices are supported.
              Empty start/end in ranges use list boundaries (e.g., ":3" or "5:").

    Returns:
        Function that takes a list and returns elements matching the spec.

    Examples:
        >>> f = gslice("0, 2:5, 7")
        >>> f(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        ['a', 'c', 'd', 'e', 'h']

        >>> g = gslice("1:3, -1")
        >>> g([10, 20, 30, 40, 50])
        [20, 30, 50]

        >>> h = gslice(":2, -2:")
        >>> h(['x', 'y', 'z', 'w'])
        ['x', 'y', 'z', 'w']
    """
    # Parse the spec string
    parts = [p.strip() for p in spec.split(',')]

    def slicer(lst: List[Any]) -> List[Any]:
        result = []
        for part in parts:
            if ':' in part:
                # Range slice
                slice_parts = part.split(':', 1)
                start_str = slice_parts[0].strip()
                end_str = slice_parts[1].strip()

                start = int(start_str) if start_str else None
                end = int(end_str) if end_str else None

                result.extend(lst[start:end])
            else:
                # Individual index
                idx = int(part)
                result.append(lst[idx])
        return result

    return slicer
