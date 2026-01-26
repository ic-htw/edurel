"""Tests for Conversation class and log_conversation method."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock
import pytest
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from edurel.utils.conversation import Conversation


@pytest.fixture
def mock_model():
    """Create a mock chat model for testing."""
    model = Mock()
    # Mock the invoke method to return an AI response
    mock_response = AIMessage(content="This is a test response")
    model.invoke.return_value = mock_response
    return model


@pytest.fixture
def chat_instance(mock_model):
    """Create an Conversation instance with a mock model."""
    return Conversation(mock_model)


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_log_conversation_creates_directory_hierarchy(chat_instance, temp_log_dir):
    """Test that log_conversation creates the full directory hierarchy."""
    # Add some messages to the conversation
    chat_instance.set_system_prompt("You are a helpful assistant")
    chat_instance.add_user_message("Hello")

    # Log the conversation
    file_path = chat_instance.log_conversation(
        temp_log_dir, "level1", "level2", "level3", "level4"
    )

    # Verify the directory structure was created
    expected_dir = Path(temp_log_dir) / "level1" / "level2" / "level3" / "level4"
    assert expected_dir.exists()
    assert expected_dir.is_dir()


def test_log_conversation_creates_json_file(chat_instance, temp_log_dir):
    """Test that log_conversation creates a JSON file."""
    # Add some messages
    chat_instance.set_system_prompt("You are a helpful assistant")
    chat_instance.add_user_message("Hello")

    # Log the conversation
    file_path = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Verify the file was created
    assert os.path.exists(file_path)
    assert file_path.endswith(".json")


def test_log_conversation_filename_format(chat_instance, temp_log_dir):
    """Test that the filename follows the timestamp format."""
    chat_instance.set_system_prompt("Test")
    chat_instance.add_user_message("Hi")

    file_path = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Extract filename
    filename = Path(file_path).name

    # Check format: yyyy_mm_dd___HH_MM_SS.json
    # Example: 2026_01_21___14_30_45.json
    parts = filename.replace(".json", "").split("___")
    assert len(parts) == 2

    # Check date part (yyyy_mm_dd)
    date_part = parts[0]
    date_parts = date_part.split("_")
    assert len(date_parts) == 3
    assert len(date_parts[0]) == 4  # year
    assert len(date_parts[1]) == 2  # month
    assert len(date_parts[2]) == 2  # day

    # Check time part (HH_MM_SS)
    time_part = parts[1]
    time_parts = time_part.split("_")
    assert len(time_parts) == 3
    assert len(time_parts[0]) == 2  # hour
    assert len(time_parts[1]) == 2  # minute
    assert len(time_parts[2]) == 2  # second


def test_log_conversation_json_content(chat_instance, temp_log_dir):
    """Test that the JSON file contains the correct conversation data."""
    # Create a conversation
    chat_instance.set_system_prompt("You are a helpful assistant")
    chat_instance.add_user_message("What is 2+2?")

    # Log the conversation
    file_path = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Read and verify the JSON content
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify structure
    assert isinstance(data, list)
    assert len(data) == 3  # system, user, ai

    # Check message types and content
    assert data[0]["type"] == "system"
    assert data[0]["content"] == "You are a helpful assistant"

    assert data[1]["type"] == "user"
    assert data[1]["content"] == "What is 2+2?"

    assert data[2]["type"] == "ai"
    assert "test response" in data[2]["content"].lower()


def test_log_conversation_stores_only_on_fourth_level(chat_instance, temp_log_dir):
    """Test that conversation files are stored only on the fourth level."""
    chat_instance.set_system_prompt("Test")

    file_path = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Verify the file is in the fourth level directory
    path_parts = Path(file_path).parts
    log_dir_parts = Path(temp_log_dir).parts

    # The file should be at: temp_log_dir/l1/l2/l3/l4/filename.json
    relative_parts = path_parts[len(log_dir_parts):]
    assert len(relative_parts) == 5  # l1, l2, l3, l4, filename.json
    assert relative_parts[0] == "l1"
    assert relative_parts[1] == "l2"
    assert relative_parts[2] == "l3"
    assert relative_parts[3] == "l4"


def test_log_conversation_creates_missing_directories(temp_log_dir):
    """Test that log_conversation creates directories if they don't exist."""
    # Create a chat instance
    model = Mock()
    model.invoke.return_value = AIMessage(content="Response")
    chat = Conversation(model)

    chat.set_system_prompt("Test")

    # Use a non-existent directory path
    non_existent_path = Path(temp_log_dir) / "new" / "path"
    assert not non_existent_path.exists()

    # Log the conversation
    file_path = chat.log_conversation(
        temp_log_dir, "new", "path", "sub", "level"
    )

    # Verify the directory was created
    expected_dir = Path(temp_log_dir) / "new" / "path" / "sub" / "level"
    assert expected_dir.exists()
    assert os.path.exists(file_path)


def test_log_conversation_returns_full_path(chat_instance, temp_log_dir):
    """Test that log_conversation returns the full path to the saved file."""
    chat_instance.set_system_prompt("Test")

    file_path = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Verify the returned path is absolute and valid
    assert os.path.isabs(file_path)
    assert os.path.exists(file_path)


def test_log_conversation_multiple_calls_create_different_files(chat_instance, temp_log_dir):
    """Test that multiple calls create different timestamped files."""
    import time

    chat_instance.set_system_prompt("Test")

    # Create first log
    file_path1 = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Wait a bit to ensure different timestamp
    time.sleep(1.1)

    # Create second log
    file_path2 = chat_instance.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Verify different files were created
    assert file_path1 != file_path2
    assert os.path.exists(file_path1)
    assert os.path.exists(file_path2)


def test_log_conversation_empty_conversation(temp_log_dir):
    """Test logging an empty conversation."""
    model = Mock()
    chat = Conversation(model)

    # Log empty conversation
    file_path = chat.log_conversation(
        temp_log_dir, "l1", "l2", "l3", "l4"
    )

    # Verify file exists and contains empty list
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 0
