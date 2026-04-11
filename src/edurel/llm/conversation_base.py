from IPython.display import Markdown, display
from typing import List, Union, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
)

from edurel.utils.misc import gslice


class Conversation:
    def __init__(self):
        self.messages: List[BaseMessage] = []

    @classmethod
    def create(cls):
         return cls()

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

    def set_system_prompt(self, prompt: str):
        system_msg = SystemMessage(content=prompt)

        # Check if there's already a system message
        if self.messages and isinstance(self.messages[0], SystemMessage):
            self.messages[0] = system_msg
        else:
            self.messages.insert(0, system_msg)

    def call_llm(self, model: BaseChatModel, prompt: str) -> str:
        # Add user message
        user_msg = HumanMessage(content=prompt)
        self.messages.append(user_msg)

        try:
            ai_response = model.invoke(self.messages)
        except Exception as e:
            ai_response = AIMessage(content=f"err: {str(e)}")

        self.messages.append(ai_response)
        return ai_response.content
    
    def gen_prompt(self, gslice_spec: str = None) -> str:
        if gslice_spec is None:
            messages_to_use = self.messages
        else:
            slicer = gslice(gslice_spec)
            messages_to_use = slicer(self.messages)
        output = [msg.content for msg in messages_to_use]
        output_str = "\n".join(output)
        return output_str
    
    def get_message(self, index: int) -> Optional[BaseMessage]:
        try:
            return self.messages[index]
        except IndexError:
            return None

    def get_messages_by_gslice(self, spec: str) -> List[BaseMessage]:
        slicer = gslice(spec)
        return slicer(self.messages)
    
    def get_all_messages(self) -> List[BaseMessage]:
        return self.messages.copy()

    def delete_message(self, index: int) -> bool:
        try:
            del self.messages[index]
            return True
        except IndexError:
            return False

    def delete_messages_by_indices(self, indices: List[int]) -> int:
        # Sort indices in reverse order to avoid index shifting issues
        sorted_indices = sorted(set(indices), reverse=True)
        deleted_count = 0

        for idx in sorted_indices:
            if self.delete_message(idx):
                deleted_count += 1

        return deleted_count

    def delete_messages_by_slice(
        self, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None
    ) -> int:
        """
        Delete a slice of messages from the conversation chain.

        Uses Python's slice notation to delete a range of messages.
        Supports negative indexing and step values.

        Args:
            start: Starting index (inclusive). None means start from beginning.
            stop: Ending index (exclusive). None means go to end.
            step: Step value. None defaults to 1.

        Returns:
            Number of messages successfully deleted.

        Examples:
            >>> conv.delete_slice(1, 3)  # Delete messages at indices 1 and 2
            >>> conv.delete_slice(2)     # Delete from index 2 to end
            >>> conv.delete_slice(None, -1)  # Delete all except last message
            >>> conv.delete_slice(0, None, 2)  # Delete every other message starting from 0
        """
        # Calculate the indices that will be deleted by the slice
        slice_obj = slice(start, stop, step)
        indices_to_delete = list(range(len(self.messages)))[slice_obj]

        # Use the existing delete_messages method to handle deletion
        return self.delete_messages(indices_to_delete)

    def clear_messages(self, keep_system: bool = True):
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

    def len(self) -> int:
        """
        Get the number of messages in the conversation.

        Returns:
            The count of messages in the conversation history.
        """
        return len(self.messages)

    def display(self, lastn_only: Optional[int] = None) -> None:
        output = []
        messages_to_show = self.messages if lastn_only is None else self.messages[-lastn_only:]
        start_index = 0 if lastn_only is None else max(0, len(self.messages) - lastn_only)

        for i, msg in enumerate(messages_to_show, start=start_index):
            msg_type = self._get_message_type(msg)
            content = msg.content
            output.append(f"[{i}] {msg_type}:\n\n{content}")

        output_str = "\n\n".join(output)
        display(Markdown(output_str))
