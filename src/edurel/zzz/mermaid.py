import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
import ipywidgets as widgets
from IPython.display import display, HTML
import subprocess
import tempfile
import edurel.zzz.yaml_utils as yu

def schema_mermaid_png(
        yaml_schema: str,
        output_path: str,
        omit_tags: Optional[List[str]] = None,
        direction: str = "TB",
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: float = 1.0
    ) -> None:

        # Get Mermaid code
        mermaid_code = yu.yaml_to_mermaid(yaml.safe_load(yaml_schema))

        # Create a temporary file for the Mermaid code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp_file:
            tmp_file.write(mermaid_code)
            tmp_mmd_path = tmp_file.name

        try:
            # Build mmdc command
            cmd = ['mmdc', '-i', tmp_mmd_path, '-o', output_path]

            # Add optional parameters
            if width is not None:
                cmd.extend(['-w', str(width)])
            if height is not None:
                cmd.extend(['-H', str(height)])
            if scale != 1.0:
                cmd.extend(['-s', str(scale)])

            # Convert to PNG using mmdc (mermaid-cli)
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "mermaid-cli (mmdc) is not installed. "
                    "Install it with: npm install -g @mermaid-js/mermaid-cli"
                ) from None
        finally:
            # Clean up temporary file
            Path(tmp_mmd_path).unlink(missing_ok=True)

