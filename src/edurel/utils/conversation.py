"""
LLM Chat utilities using LangChain and LangGraph.

This module provides a class for managing conversations with large language models,
with support for conversation history tracking and manipulation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Union, Optional, Sequence
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

import edurel.utils.misc as mu

# ---------------------------------------------------------------------------------------------
# Chat Clients
# ---------------------------------------------------------------------------------------------
def anthropic_client(model, timeout=60, max_retries=0, temperature=0):
    return ChatAnthropic(
        model=model,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )

def stats_client(model, timeout=60, max_retries=0, temperature=0):
    return ChatOpenAI(
        model=model,
        api_key=os.getenv("LLM_STATS_API_KEY"),
        base_url="https://api.zeroeval.com/v1",
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )

def ollama_client(model, timeout=60, max_retries=0, temperature=0):
    return ChatOllama(
        model=model,
        # validate_model_on_init=True,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
        base_url=os.getenv("OLLAMA_API_URL"),
        client_kwargs={"verify": False},
    )

def openai_client(model, timeout=60, max_retries=0, temperature=0):
    return ChatOpenAI(
        model=model,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )

# ---------------------------------------------------------------------------------------------
# LLM Names
# ---------------------------------------------------------------------------------------------
ARCTICTEXT2SQL = "a-kore/Arctic-Text2SQL-R1-7B"
DEEPSEEK32 = "deepseek-chat"
DEEPSEEK32THINKING = "deepseek-reasoner"
DEEPSEEK32EXP = "deepseek-v3.2-exp"
GEMINI25FLASH ="gemini-2.5-flash"
GEMINI25PRO ="gemini-2.5-pro"
GEMINI3PRO ="gemini-3-pro-preview"
GEMINI3FLASH ="gemini-3-flash-preview"
GLM46 = "glm-4.6"
GLM47 = "glm-4.7"
GPT41MINI = "gpt-4.1-mini-2025-04-14"
GPT5 = "gpt-5-2025-08-07"
GPT5MINI = "gpt-5-mini-2025-08-07"
GROK4 = "grok-4"
KIMIK2 = "kimi-k2-0905"
OPUS41 = "claude-opus-4-1-20250805"
OPUS45 = "claude-opus-4-5-20251101"
SONNET4 ="claude-sonnet-4-20250514"
SONNET45 ="claude-sonnet-4-5-20250929"

# ---------------------------------------------------------------------------------------------
# class MessagesState:
# ---------------------------------------------------------------------------------------------
class MessagesState(TypedDict):
    """State schema for conversation messages."""

    messages: Sequence[BaseMessage]


# ---------------------------------------------------------------------------------------------
# class Conversation:
# ---------------------------------------------------------------------------------------------
class Conversation:
    """
    A class for managing conversations with a large language model.

    This class provides methods to track conversation history, set system prompts,
    add user messages, and manipulate the conversation chain.

    Attributes:
        model: The LangChain chat model to use for generating responses.
        messages: List of conversation messages (SystemMessage, HumanMessage, AIMessage).
    """

    def __init__(self, model: BaseChatModel):
        """
        Initialize the LLMChat with a LangChain model.

        Args:
            model: A LangChain BaseChatModel instance (e.g., ChatOpenAI, ChatAnthropic).
        """
        self.model = model
        self.messages: List[BaseMessage] = []
        self._graph = None
        self._setup_graph()

    def _setup_graph(self):
        """Set up the LangGraph conversation graph."""

        def call_model(state: MessagesState):
            """Call the model with the current conversation history."""
            response = self.model.invoke(state["messages"])
            return {"messages": [response]}

        # Create the graph
        workflow = StateGraph(MessagesState)
        workflow.add_node("model", call_model)
        workflow.set_entry_point("model")
        workflow.add_edge("model", END)

        self._graph = workflow.compile()

    def set_system_prompt(self, prompt: str):
        """
        Set or update the system prompt.

        If a system message already exists, it will be replaced.
        Otherwise, a new system message is added at the beginning.

        Args:
            prompt: The system prompt text.
        """
        system_msg = SystemMessage(content=prompt)

        # Check if there's already a system message
        if self.messages and isinstance(self.messages[0], SystemMessage):
            self.messages[0] = system_msg
        else:
            self.messages.insert(0, system_msg)

    def add_user_message(self, message: str) -> str:
        """
        Add a user message and get the AI's response.

        Args:
            message: The user's message text.

        Returns:
            The AI's response text.
        """
        # Add user message
        user_msg = HumanMessage(content=message)
        self.messages.append(user_msg)

        try:
            # Get AI response using the graph
            result = self._graph.invoke({"messages": self.messages})
        except Exception as e:
            return f"err: {str(e)}"

        ai_response = result["messages"][-1]
        self.messages.append(ai_response)
        return ai_response.content

    def get_messages(self) -> List[BaseMessage]:
        """
        Get the complete conversation history.

        Returns:
            List of all messages in the conversation.
        """
        return self.messages.copy()

    def show_conversation(self, lastn_only: Optional[int] = None) -> str:
        """
        Display the complete conversation chain with message type indicators.

        Args:
            lastn_only: If provided, show only the last n entries. If None, show all.

        Returns:
            A formatted string showing the conversation with types.
        """
        output = []
        messages_to_show = self.messages if lastn_only is None else self.messages[-lastn_only:]
        start_index = 0 if lastn_only is None else max(0, len(self.messages) - lastn_only)

        for i, msg in enumerate(messages_to_show, start=start_index):
            msg_type = self._get_message_type(msg)
            content = msg.content
            output.append(f"[{i}] {msg_type}:\n {content}")

        return "\n\n".join(output)

    def _get_message_type(self, message: BaseMessage) -> str:
        """Get the type label for a message."""
        if isinstance(message, SystemMessage):
            return "SYSTEM"
        elif isinstance(message, HumanMessage):
            return "USER"
        elif isinstance(message, AIMessage):
            return "AI"
        else:
            return "UNKNOWN"

    def get_message(self, index: int) -> Optional[BaseMessage]:
        """
        Select a single message from the conversation chain by index.

        Args:
            index: The index of the message (supports negative indexing).

        Returns:
            The message at the specified index, or None if index is out of range.
        """
        try:
            return self.messages[index]
        except IndexError:
            return None

    def get_messages_by_indices(self, indices: List[int]) -> List[BaseMessage]:
        """
        Select multiple messages from the conversation chain by their indices.

        Args:
            indices: List of message indices to retrieve.

        Returns:
            List of messages at the specified indices (skips invalid indices).
        """
        selected = []
        for idx in indices:
            msg = self.get_message(idx)
            if msg is not None:
                selected.append(msg)
        return selected

    def delete_message(self, index: int) -> bool:
        """
        Delete a message from the conversation chain.

        Args:
            index: The index of the message to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            del self.messages[index]
            return True
        except IndexError:
            return False

    def delete_messages(self, indices: List[int]) -> int:
        """
        Delete multiple messages from the conversation chain.

        Args:
            indices: List of message indices to delete.

        Returns:
            Number of messages successfully deleted.
        """
        # Sort indices in reverse order to avoid index shifting issues
        sorted_indices = sorted(set(indices), reverse=True)
        deleted_count = 0

        for idx in sorted_indices:
            if self.delete_message(idx):
                deleted_count += 1

        return deleted_count

    def insert_message(
        self, index: int, message: Union[str, BaseMessage], msg_type: str = "user"
    ) -> bool:
        """
        Insert a message at a specific position in the conversation chain.

        Args:
            index: The position to insert the message.
            message: The message content (string) or a BaseMessage object.
            msg_type: Type of message ('system', 'user', or 'ai') if message is a string.

        Returns:
            True if insertion was successful, False otherwise.
        """
        if isinstance(message, str):
            # Create appropriate message type
            if msg_type.lower() == "system":
                msg_obj = SystemMessage(content=message)
            elif msg_type.lower() == "ai":
                msg_obj = AIMessage(content=message)
            else:  # default to user
                msg_obj = HumanMessage(content=message)
        else:
            msg_obj = message

        try:
            self.messages.insert(index, msg_obj)
            return True
        except (IndexError, TypeError):
            return False

    def insert_message_at_end(
        self, message: Union[str, BaseMessage], msg_type: str = "user"
    ) -> bool:
        self.insert_message(len(self.messages), message, msg_type)

    def replace_message(
        self, index: int, message: Union[str, BaseMessage], msg_type: str = "user"
    ) -> bool:
        """
        Replace a message at a specific position in the conversation chain.

        Args:
            index: The position of the message to replace.
            message: The new message content (string) or a BaseMessage object.
            msg_type: Type of message ('system', 'user', or 'ai') if message is a string.

        Returns:
            True if replacement was successful, False otherwise.
        """
        if isinstance(message, str):
            # Create appropriate message type
            if msg_type.lower() == "system":
                msg_obj = SystemMessage(content=message)
            elif msg_type.lower() == "ai":
                msg_obj = AIMessage(content=message)
            else:  # default to user
                msg_obj = HumanMessage(content=message)
        else:
            msg_obj = message

        try:
            self.messages[index] = msg_obj
            return True
        except IndexError:
            return False

    def clear_conversation(self, keep_system: bool = True):
        """
        Clear the conversation history.

        Args:
            keep_system: If True, keeps the system message (if present).
        """
        if keep_system and self.messages and isinstance(self.messages[0], SystemMessage):
            system_msg = self.messages[0]
            self.messages = [system_msg]
        else:
            self.messages = []

    def get_conversation_length(self) -> int:
        """
        Get the number of messages in the conversation.

        Returns:
            The count of messages in the conversation history.
        """
        return len(self.messages)

    def export_conversation(self) -> List[dict]:
        """
        Export the conversation as a list of dictionaries.

        Returns:
            List of message dictionaries with 'type' and 'content' keys.
        """
        exported = []
        for msg in self.messages:
            exported.append(
                {"type": self._get_message_type(msg).lower(), "content": msg.content}
            )
        return exported

    def log_conversation(
        self, log_dir: str, l1: str, l2: str, l3: str, l4: str
    ) -> str:
        """
        Log the conversation to a JSON file in a hierarchical directory structure.

        Creates a four-level directory hierarchy and stores the conversation
        as a JSON file with a timestamp-based filename.

        Args:
            log_dir: Root directory for the log file hierarchy.
            l1: First level subdirectory name.
            l2: Second level subdirectory name.
            l3: Third level subdirectory name.
            l4: Fourth level subdirectory name.

        Returns:
            The full path to the saved log file.

        Example:
            >>> chat.log_conversation("/logs", "project1", "session1", "user1", "v1")
            # Creates: /logs/project1/session1/user1/v1/2026_01_21___14_30_45.json
        """
        # Build the full directory path
        full_path = Path(log_dir) / l1 / l2 / l3 / l4

        # Create directories if they don't exist
        full_path.mkdir(parents=True, exist_ok=True)

        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y_%m_%d___%H_%M_%S")
        filename = f"{timestamp}.json"
        file_path = full_path / filename

        # Export conversation and save to JSON
        conversation_data = self.export_conversation()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        return str(file_path)
