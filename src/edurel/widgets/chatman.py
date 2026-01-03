"""
ChatMan - Interactive conversation manager widget for LLM chats.

Provides a Jupyter notebook widget for managing conversations with large language models,
including conversation history tracking, message manipulation, and import/export functionality.
"""

import json
from pathlib import Path
from typing import Optional
import ipywidgets as widgets
from IPython.display import display
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from edurel.utils.llmchat import LLMChat


class ChatMan:
    """
    Interactive conversation manager for LLM chats in Jupyter notebooks.

    Provides a UI for managing conversation history, manipulating messages,
    and importing/exporting conversations to JSON files.
    """

    def __init__(self, chat: LLMChat, chat_path: Optional[str] = None):
        """
        Initialize ChatMan widget.

        Args:
            chat: An instance of LLMChat for managing the conversation.
            chat_path: Optional path to folder where chats should be stored.
        """
        self.chat = chat
        self.chat_path = Path(chat_path) if chat_path else Path(".")
        self.chat_path.mkdir(parents=True, exist_ok=True)

        self._create_widgets()
        self._setup_layout()
        self._update_display()

    def _create_widgets(self):
        """Create all UI widgets."""
        # Directory picker section
        self.directory_input = widgets.Text(
            value=str(self.chat_path),
            description="Directory:",
            layout=widgets.Layout(width="70%")
        )

        self.directory_btn = widgets.Button(
            description="Set Directory",
            button_style="primary",
            icon="folder",
            layout=widgets.Layout(width="28%")
        )

        # File operations section
        self.filename_input = widgets.Text(
            value="conversation.json",
            description="Filename:",
            layout=widgets.Layout(width="60%")
        )

        self.save_btn = widgets.Button(
            description="Save",
            button_style="success",
            icon="save",
            layout=widgets.Layout(width="18%")
        )

        self.load_btn = widgets.Button(
            description="Load",
            button_style="info",
            icon="upload",
            layout=widgets.Layout(width="18%")
        )

        self.clear_btn = widgets.Button(
            description="Clear All",
            button_style="danger",
            icon="trash",
            layout=widgets.Layout(width="100%")
        )

        # User input section
        self.user_input = widgets.Textarea(
            placeholder="Enter your message...",
            layout=widgets.Layout(width="100%", height="120px")
        )

        self.send_btn = widgets.Button(
            description="Send",
            button_style="primary",
            icon="paper-plane",
            layout=widgets.Layout(width="100%")
        )

        # System prompt section
        self.system_label = widgets.Label("System Message:")
        self.system_input = widgets.Textarea(
            placeholder="Enter system prompt...",
            layout=widgets.Layout(width="85%", height="150px")
        )

        self.system_update_btn = widgets.Button(
            description="Update",
            button_style="warning",
            icon="refresh",
            layout=widgets.Layout(width="13%")
        )

        # Conversation display container
        self.conversation_container = widgets.VBox(
            # layout=widgets.Layout(
            #     width="100%",
            #     height="600px",
            #     overflow_y="auto",
            #     border="1px solid #ccc"
            # )
        )

        # Output for messages
        self.output = widgets.Output()

        # Set up event handlers
        self.directory_btn.on_click(self._on_set_directory)
        self.save_btn.on_click(self._on_save)
        self.load_btn.on_click(self._on_load)
        self.clear_btn.on_click(self._on_clear)
        self.send_btn.on_click(self._on_send)
        self.system_update_btn.on_click(self._on_update_system)

    def _setup_layout(self):
        """Set up the widget layout."""
        # Directory picker row
        directory_row = widgets.HBox([
            self.directory_input,
            self.directory_btn
        ])

        # File operations row
        file_ops_row = widgets.HBox([
            self.filename_input,
            self.save_btn,
            self.load_btn
        ])
        file_ops = widgets.VBox([
            directory_row,
            file_ops_row,
            self.clear_btn
        ])

        # System prompt section
        system_row = widgets.HBox([
            self.system_input,
            self.system_update_btn
        ])
        system_section = widgets.VBox([
            self.system_label,
            system_row
        ])

        # User input section
        user_section = widgets.VBox([
            widgets.Label("Your Message:"),
            self.user_input,
            self.send_btn
        ])

        # Conversation section
        conversation_section = widgets.VBox([
            widgets.Label("Conversation History:"),
            self.conversation_container
        ])

        # Main layout
        self.main_layout = widgets.VBox([
            file_ops,
            widgets.HTML("<hr>"),
            system_section,
            widgets.HTML("<hr>"),
            user_section,
            widgets.HTML("<hr>"),
            conversation_section,
            self.output
        ])

    def _update_display(self):
        """Update the conversation display."""
        messages = self.chat.get_messages()
        message_widgets = []

        # Update system prompt if present
        if messages and isinstance(messages[0], SystemMessage):
            self.system_input.value = messages[0].content
        else:
            self.system_input.value = ""

        # Create widgets for each message
        for idx, msg in enumerate(messages):
            msg_widget = self._create_message_widget(idx, msg)
            message_widgets.append(msg_widget)

        self.conversation_container.children = message_widgets

    def _create_message_widget(self, idx: int, msg):
        """Create a widget for a single message."""
        # Determine message type and label
        if isinstance(msg, SystemMessage):
            msg_type = "S"
            label_style = "info"
        elif isinstance(msg, HumanMessage):
            msg_type = "U"
            label_style = "success"
        elif isinstance(msg, AIMessage):
            msg_type = "A"
            label_style = "warning"
        else:
            msg_type = "?"
            label_style = ""

        # Message type label
        type_label = widgets.Button(
            description=msg_type,
            disabled=True,
            button_style=label_style,
            layout=widgets.Layout(width="40px", height="auto")
        )

        # Message content textarea - calculate height based on content
        content_lines = msg.content.count('\n') + 1
        textarea_height = max(80, min(300, content_lines * 20 + 20))

        msg_textarea = widgets.Textarea(
            value=msg.content,
            layout=widgets.Layout(width="70%", height=f"{textarea_height}px")
        )

        # Replace button
        replace_btn = widgets.Button(
            description="Replace",
            button_style="",
            icon="edit",
            layout=widgets.Layout(width="13%")
        )
        replace_btn.on_click(lambda _b, i=idx, ta=msg_textarea: self._on_replace(i, ta))

        # Delete button
        delete_btn = widgets.Button(
            description="Delete",
            button_style="danger",
            icon="trash",
            layout=widgets.Layout(width="13%")
        )
        delete_btn.on_click(lambda _b, i=idx: self._on_delete(i))

        # Arrange widgets horizontally
        msg_row = widgets.HBox([
            type_label,
            msg_textarea,
            replace_btn,
            delete_btn
        ])

        return msg_row

    def _on_send(self, _button):
        """Handle send button click."""
        user_message = self.user_input.value.strip()

        if not user_message:
            with self.output:
                print("Error: Cannot send empty message")
            return

        try:
            # Add user message and get AI response
            with self.output:
                print("Sending message...")

            response = self.chat.add_user_message(user_message)

            # Clear input and update display
            self.user_input.value = ""
            self._update_display()

            with self.output:
                self.output.clear_output()
                print(f"Response received: {len(response)} characters")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error sending message: {e}")

    def _on_update_system(self, _button):
        """Handle system prompt update button click."""
        system_prompt = self.system_input.value.strip()

        try:
            self.chat.set_system_prompt(system_prompt)
            self._update_display()

            with self.output:
                self.output.clear_output()
                print("System prompt updated")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error updating system prompt: {e}")

    def _on_replace(self, index: int, textarea: widgets.Textarea):
        """Handle replace button click."""
        new_content = textarea.value
        messages = self.chat.get_messages()

        if index >= len(messages):
            with self.output:
                self.output.clear_output()
                print(f"Error: Invalid message index {index}")
            return

        # Determine message type
        msg = messages[index]
        if isinstance(msg, SystemMessage):
            msg_type = "system"
        elif isinstance(msg, AIMessage):
            msg_type = "ai"
        else:
            msg_type = "user"

        try:
            success = self.chat.replace_message(index, new_content, msg_type)

            if success:
                self._update_display()
                with self.output:
                    self.output.clear_output()
                    print(f"Message {index} replaced")
            else:
                with self.output:
                    self.output.clear_output()
                    print(f"Error: Failed to replace message {index}")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error replacing message: {e}")

    def _on_delete(self, index: int):
        """Handle delete button click."""
        try:
            success = self.chat.delete_message(index)

            if success:
                self._update_display()
                with self.output:
                    self.output.clear_output()
                    print(f"Message {index} deleted")
            else:
                with self.output:
                    self.output.clear_output()
                    print(f"Error: Failed to delete message {index}")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error deleting message: {e}")

    def _on_set_directory(self, _button):
        """Handle set directory button click."""
        directory = self.directory_input.value.strip()

        if not directory:
            with self.output:
                self.output.clear_output()
                print("Error: Directory cannot be empty")
            return

        try:
            new_path = Path(directory)
            new_path.mkdir(parents=True, exist_ok=True)
            self.chat_path = new_path
            self.directory_input.value = str(self.chat_path)

            with self.output:
                self.output.clear_output()
                print(f"Directory set to: {self.chat_path}")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error setting directory: {e}")

    def _on_save(self, _button):
        """Handle save button click."""
        filename = self.filename_input.value.strip()

        if not filename:
            with self.output:
                self.output.clear_output()
                print("Error: Filename cannot be empty")
            return

        filepath = self.chat_path / filename

        try:
            conversation_data = self.chat.export_conversation()

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            with self.output:
                self.output.clear_output()
                print(f"Conversation saved to {filepath}")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error saving conversation: {e}")

    def _on_load(self, _button):
        """Handle load button click."""
        filename = self.filename_input.value.strip()

        if not filename:
            with self.output:
                self.output.clear_output()
                print("Error: Filename cannot be empty")
            return

        filepath = self.chat_path / filename

        if not filepath.exists():
            with self.output:
                self.output.clear_output()
                print(f"Error: File {filepath} does not exist")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)

            self.import_conversation(conversation_data)

            with self.output:
                self.output.clear_output()
                print(f"Conversation loaded from {filepath}")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error loading conversation: {e}")

    def _on_clear(self, _button):
        """Handle clear all button click."""
        try:
            self.chat.clear_conversation(keep_system=False)
            self._update_display()

            with self.output:
                self.output.clear_output()
                print("Conversation cleared")

        except Exception as e:
            with self.output:
                self.output.clear_output()
                print(f"Error clearing conversation: {e}")

    def export_conversation(self):
        """
        Export the complete conversation chain.

        Returns:
            List of message dictionaries with 'type' and 'content' keys.
        """
        return self.chat.export_conversation()

    def import_conversation(self, conversation_data):
        """
        Import a complete conversation chain.

        Args:
            conversation_data: List of message dictionaries with 'type' and 'content' keys.
        """
        # Clear existing conversation
        self.chat.messages = []

        # Import messages
        for msg_dict in conversation_data:
            msg_type = msg_dict.get("type", "user").lower()
            content = msg_dict.get("content", "")

            if msg_type == "system":
                msg = SystemMessage(content=content)
            elif msg_type == "ai":
                msg = AIMessage(content=content)
            else:  # default to user
                msg = HumanMessage(content=content)

            self.chat.messages.append(msg)

        # Update display
        self._update_display()

    def display(self):
        """Display the ChatMan widget."""
        display(self.main_layout)
