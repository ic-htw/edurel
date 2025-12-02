"""
Mermaid Visualization Widget

A simple Jupyter notebook widget for visualizing Mermaid diagrams.
"""
from typing import Optional
import ipywidgets as widgets
from IPython.display import display, HTML


class MermaidVisualizer:
    """
    A widget for visualizing Mermaid diagrams from code.

    Features:
    - Text input pane for entering Mermaid diagram code
    - Button to render the diagram
    - Graphical output pane displaying the rendered diagram
    """

    def __init__(self, initial_code: str = ""):
        """
        Initialize the MermaidVisualizer widget.

        Args:
            initial_code: Optional initial Mermaid code to display
        """
        self.mermaid_code: str = initial_code

        # Create UI components
        self._create_widgets()
        self._setup_handlers()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Text input pane for Mermaid code
        self.text_input = widgets.Textarea(
            value=self.mermaid_code,
            placeholder='Enter Mermaid diagram code here...\n\nExample:\ngraph TD\n    A[Start] --> B[End]',
            description='',
            layout=widgets.Layout(width='100%', height='300px')
        )

        # Button to visualize
        self.visualize_button = widgets.Button(
            description='Visualize Diagram',
            button_style='success',
            icon='eye',
            layout=widgets.Layout(width='200px')
        )

        # Graphical output pane
        self.graph_output = widgets.Output(
            layout=widgets.Layout(width='100%', height='500px', border='1px solid #ddd')
        )

    def _setup_handlers(self):
        """Set up event handlers for buttons."""
        self.visualize_button.on_click(self._on_visualize)

    def _on_visualize(self, _):
        """Visualize the Mermaid diagram when button is clicked."""
        self.graph_output.clear_output()

        # Get code from text input
        self.mermaid_code = self.text_input.value.strip()

        if not self.mermaid_code:
            with self.graph_output:
                print("⚠️  No diagram code provided")
            return

        try:
            html_content = self._create_mermaid_html(self.mermaid_code)

            with self.graph_output:
                display(HTML(html_content))

        except Exception as e:
            with self.graph_output:
                print(f"❌ Error visualizing diagram: {e}")

    def _create_mermaid_html(self, mermaid_code: str) -> str:
        """
        Create HTML with Mermaid.js to render the diagram.

        Args:
            mermaid_code: Mermaid diagram code

        Returns:
            HTML string with embedded Mermaid diagram
        """
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
        input_section = widgets.VBox([
            widgets.HTML("<h3>Mermaid Code</h3>"),
            self.text_input,
            self.visualize_button
        ])

        output_section = widgets.VBox([
            widgets.HTML("<h3>Diagram Output</h3>"),
            self.graph_output
        ])

        main_layout = widgets.VBox([
            widgets.HTML("<h2>Mermaid Diagram Visualizer</h2>"),
            input_section,
            widgets.HTML("<hr>"),
            output_section
        ])

        display(main_layout)

    def set_code(self, code: str):
        """
        Set the Mermaid code programmatically.

        Args:
            code: Mermaid diagram code
        """
        self.text_input.value = code
        self.mermaid_code = code
