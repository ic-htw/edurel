import re
from pathlib import Path
from typing import Optional
import uuid
import subprocess
import tempfile

from IPython.display import HTML, display

def display_mermaid_diagram(mermaid_code, width="100%", height="500px") -> None:
    div_id = "mermaid_" + uuid.uuid4().hex
    html_content = f"""
    <div style="width: {width}; height: {height}; overflow: auto; border: 1px solid #ddd;">
        <div id="{div_id}" class="mermaid">
            {mermaid_code}
        </div>
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

        mermaid.initialize({{
            startOnLoad: false,
            theme: 'default',
            securityLevel: 'loose'
        }});

        const element = document.getElementById('{div_id}');
        if (element) {{
            try {{
                element.removeAttribute('data-processed');
                await mermaid.run({{ nodes: [element] }});
                console.log('Mermaid diagram rendered successfully: {div_id}');
            }} catch (err) {{
                console.error('Mermaid rendering error:', err);
                element.innerHTML = '<pre style="color:red;">❌ Error rendering diagram:\\n' + err.message + '</pre>';
            }}
        }} else {{
            console.error('Element not found: {div_id}');
        }}
    </script>
    """
    display(HTML(html_content))


def save_mermaid_png(
    mermaid_code: str,
    output_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: float = 1.0
) -> None:
    """Save Mermaid diagram code as PNG file using mermaid-cli.

    Args:
        mermaid_code: Mermaid diagram code to render
        output_path: Path where PNG file will be saved
        width: Optional width in pixels
        height: Optional height in pixels
        scale: Scale factor for rendering (default: 1.0)

    Raises:
        FileNotFoundError: If mermaid-cli (mmdc) is not installed
    """
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
