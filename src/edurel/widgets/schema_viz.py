"""
Schema Visualization Widget

A Jupyter notebook widget for visualizing relational database schemas from YAML files.
"""
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
import ipywidgets as widgets
from IPython.display import display, HTML


class SchemaVisualizer:
    """
    A widget for visualizing database schemas from YAML files.

    Features:
    - File selector for loading YAML schema files
    - Convert schema to Mermaid ER diagram syntax
    - Display Mermaid code in text output
    - Render diagram visually using Mermaid.js
    """

    def __init__(self, directory: str = "."):
        """
        Initialize the SchemaVisualizer widget.

        Args:
            directory: Starting directory for file selection
        """
        self.directory = Path(directory)
        self.schema_data: Optional[Dict[str, Any]] = None
        self.mermaid_code: str = ""

        # Create UI components
        self._create_widgets()
        self._setup_handlers()

    def _create_widgets(self):
        """Create all UI widgets."""
        # File selector
        self.file_input = widgets.Text(
            value='',
            placeholder='Enter YAML file path',
            description='YAML File:',
            style={'description_width': '100px'},
            layout=widgets.Layout(width='500px')
        )

        self.load_button = widgets.Button(
            description='Load YAML',
            button_style='primary',
            icon='upload'
        )

        # Button 1: Generate Mermaid code
        self.generate_button = widgets.Button(
            description='Generate Diagram Code',
            button_style='success',
            icon='code',
            disabled=True
        )

        # Text output pane for Mermaid code
        self.text_output = widgets.Textarea(
            value='',
            placeholder='Mermaid diagram code will appear here...',
            description='',
            layout=widgets.Layout(width='100%', height='300px')
        )

        # Button 2: Visualize diagram
        self.visualize_button = widgets.Button(
            description='Visualize Diagram',
            button_style='info',
            icon='eye',
            disabled=True
        )

        # Graphical output pane
        self.graph_output = widgets.Output(
            layout=widgets.Layout(width='100%', height='500px', border='1px solid #ddd')
        )

        # Status messages
        self.status_output = widgets.Output()

    def _setup_handlers(self):
        """Set up event handlers for buttons."""
        self.load_button.on_click(self._on_load_yaml)
        self.generate_button.on_click(self._on_generate_diagram)
        self.visualize_button.on_click(self._on_visualize_diagram)

    def _on_load_yaml(self, button):
        """Load YAML file when load button is clicked."""
        self.status_output.clear_output()

        file_path = Path(self.directory) / self.file_input.value
        if not file_path.exists():
            with self.status_output:
                print(f"❌ Error: File not found: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.schema_data = yaml.safe_load(f)

            with self.status_output:
                print(f"✅ Loaded schema from: {file_path}")
                if 'tables' in self.schema_data:
                    print(f"   Found {len(self.schema_data['tables'])} tables")

            # Enable generate button
            self.generate_button.disabled = False

        except Exception as e:
            with self.status_output:
                print(f"❌ Error loading file: {e}")

    def _on_generate_diagram(self, button):
        """Generate Mermaid diagram code from schema."""
        self.status_output.clear_output()

        if not self.schema_data:
            with self.status_output:
                print("❌ No schema data loaded")
            return

        try:
            self.mermaid_code = self._schema_to_mermaid(self.schema_data)
            self.text_output.value = self.mermaid_code

            with self.status_output:
                print("✅ Generated Mermaid diagram code")

            # Enable visualize button
            self.visualize_button.disabled = False

        except Exception as e:
            with self.status_output:
                print(f"❌ Error generating diagram: {e}")

    def _on_visualize_diagram(self, button):
        """Visualize the Mermaid diagram."""
        self.graph_output.clear_output()

        if not self.mermaid_code:
            with self.status_output:
                print("❌ No diagram code to visualize")
            return

        try:
            html_content = self._create_mermaid_html(self.mermaid_code)

            with self.graph_output:
                display(HTML(html_content))

            with self.status_output:
                print("✅ Diagram rendered successfully")

        except Exception as e:
            with self.status_output:
                print(f"❌ Error visualizing diagram: {e}")

    def _schema_to_mermaid(self, schema: Dict[str, Any]) -> str:
        """
        Convert schema dictionary to Mermaid ER diagram syntax.

        Args:
            schema: Schema dictionary loaded from YAML

        Returns:
            Mermaid diagram code as string
        """
        lines = ["erDiagram"]

        tables = schema.get('tables', [])

        # Generate table definitions
        for table in tables:
            table_name = table['name']
            columns = table.get('columns', [])
            pk_cols = set(table.get('primary_key', []))

            lines.append(f"    {table_name} {{")

            for col in columns:
                col_name = col['name']
                col_type = col['type']
                nullable = col.get('nullable', True)

                # Add PK or NULL constraint markers
                constraint = ""
                if col_name in pk_cols:
                    constraint = " PK"
                elif not nullable:
                    constraint = " NOT_NULL"

                lines.append(f"        {col_type} {col_name}{constraint}")

            lines.append("    }")

        # Generate relationships from foreign keys
        for table in tables:
            table_name = table['name']
            foreign_keys = table.get('foreign_keys', [])

            for fk in foreign_keys:
                ref_table = fk['ref_table']
                fk_cols = ', '.join(fk['columns'])
                ref_cols = ', '.join(fk['ref_columns'])

                # Mermaid relationship: many-to-one (orders to users)
                # Format: SOURCE }o--|| TARGET : "relationship"
                lines.append(f'    {table_name} }}o--|| {ref_table} : "{fk_cols} -> {ref_cols}"')

        return "\n".join(lines)

    def _create_mermaid_html(self, mermaid_code: str) -> str:
        """
        Create HTML with Mermaid.js to render the diagram.

        Args:
            mermaid_code: Mermaid diagram code

        Returns:
            HTML string with embedded Mermaid diagram
        """
        # Escape any special characters in the mermaid code
        escaped_code = mermaid_code.replace('`', '\\`')

        html = f"""
        <div class="mermaid-container">
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
            </script>
            <div class="mermaid">
{mermaid_code}
            </div>
        </div>
        """
        return html

    def display(self):
        """Display the widget in the notebook."""
        # Layout
        file_box = widgets.HBox([self.file_input, self.load_button])

        button_box1 = widgets.HBox([self.generate_button])
        text_section = widgets.VBox([
            widgets.HTML("<h3>Diagram Code (Mermaid)</h3>"),
            button_box1,
            self.text_output
        ])

        button_box2 = widgets.HBox([self.visualize_button])
        graph_section = widgets.VBox([
            widgets.HTML("<h3>Visual Diagram</h3>"),
            button_box2,
            self.graph_output
        ])

        main_layout = widgets.VBox([
            widgets.HTML("<h2>Database Schema Visualizer</h2>"),
            file_box,
            self.status_output,
            widgets.HTML("<hr>"),
            text_section,
            widgets.HTML("<hr>"),
            graph_section
        ])

        display(main_layout)

    def load_from_path(self, file_path: str):
        """
        Programmatically load a YAML file.

        Args:
            file_path: Path to YAML file
        """
        self.file_input.value = file_path
        self._on_load_yaml(None)
