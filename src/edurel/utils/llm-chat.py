"""
LLM Chat utilities using LangChain and LangGraph.

This module provides a class for managing conversations with large language models,
with support for conversation history tracking and manipulation.
"""

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


class MessagesState(TypedDict):
    """State schema for conversation messages."""

    messages: Sequence[BaseMessage]


class LLMChat:
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

        # Get AI response using the graph
        result = self._graph.invoke({"messages": self.messages})
        ai_response = result["messages"][-1]

        # Add AI response to history
        self.messages.append(ai_response)

        return ai_response.content

    def get_messages(self) -> List[BaseMessage]:
        """
        Get the complete conversation history.

        Returns:
            List of all messages in the conversation.
        """
        return self.messages.copy()

    def show_conversation(self) -> str:
        """
        Display the complete conversation chain with message type indicators.

        Returns:
            A formatted string showing the conversation with types.
        """
        output = []
        for i, msg in enumerate(self.messages):
            msg_type = self._get_message_type(msg)
            content = msg.content
            output.append(f"[{i}] {msg_type}: {content}")

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
