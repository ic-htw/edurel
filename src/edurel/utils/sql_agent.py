"""SQL Agent for natural language to SQL query generation."""

from typing import Optional, List
from datetime import datetime
from .duckdb import Db
from .conversation import Conversation, Client, LLMName
from .rel_schema_man import RelSchemaMan
from .misc import sql_extract, md_plain, md_yaml


class SQLAgent:
    """Agent for converting natural language questions to SQL queries.

    This class combines a database connection, schema management, and an LLM
    conversation to provide text-to-SQL capabilities with automatic execution
    and result formatting.
    """

    def __init__(
        self,
        db: Db,
        client: Client,
        llm_name: LLMName,
        system_prompt: Optional[str] = None,
        transform_spec_file_path: Optional[str] = None,
        fk_spec_file_path: Optional[str] = None,
        rem_tags_spec_file_path: Optional[str] = None,
        log_dir: Optional[str] = None,
        autolog: bool = False,
    ):
        """Initialize SQLAgent with database, LLM, and optional transformations.

        Args:
            db: Database instance to query
            client: LLM client enum value (e.g., Client.ANTHROPIC)
            llm_name: LLM model name enum value (e.g., LLMName.SONNET45)
            system_prompt: Optional custom system prompt for the LLM
            transform_spec_file_path: Optional schema transformation specification file path
            fk_spec_file_path: Optional foreign key addition specification file path
            rem_tags_spec_file_path: Optional schema tags removal specification file path
            log_dir: Optional root directory for logging conversations
            autolog: If True, automatically log conversations after each query

        Raises:
            ValueError: If autolog is True but log_dir is not set
        """
        self.db = db
        self.model = llm_name.name
        self.log_dir = log_dir
        self.autolog = autolog

        # Validate autolog/log_dir combination
        if self.autolog and not self.log_dir:
            raise ValueError("log_dir must be set when autolog is True")

        # Create RelSchemaMan instance and apply transformations
        schema_yaml = db.yaml()
        self.schema_man = RelSchemaMan(schema_yaml)

        if transform_spec_file_path:
            self.schema_man.transform(transform_spec_file_path)

        if fk_spec_file_path:
            self.schema_man.add_fks(fk_spec_file_path)

        if rem_tags_spec_file_path:
            self.schema_man.remove_tags(rem_tags_spec_file_path)

        # Create Conversation instance
        self.conversation = Conversation.create(
            client=client,
            llm_name=llm_name
        )

        # Set system prompt
        if system_prompt is None:
            system_prompt = "You are an expert SQL query generator. Convert natural language questions into valid SQL queries. Use duckdb syntax."

        self.conversation.set_system_prompt(system_prompt)

        # Insert schema at end of conversation
        schema_text = self.schema_man.yaml()
        self.conversation.insert_message_at_end(
            f"Database Schema:\n{md_yaml(schema_text)}",
            msg_type="user"
        )

    def text2sql(self, questiontag: str, question: str) -> None:
        """Convert natural language question to SQL and execute it.

        Args:
            question: Natural language question to convert to SQL
            questiontag: Tag or identifier for the question
        """
        # Get LLM response
        response = self.conversation.add_user_message(question)

        # Check for error in response
        if "err:" in response:
            # Insert error as AI message and stop
            self.conversation.insert_message_at_end(response, msg_type="ai")
            return response

        # Extract SQL from response
        sql_code = sql_extract(response)

        if not sql_code:
            error_msg = "err: Could not extract SQL code from response"
            self.conversation.insert_message_at_end(error_msg, msg_type="ai")
            return error_msg

        # Execute SQL
        result = self.db.eval_nx(sql_code)

        # Insert result as markdown plaintext
        result_formatted = md_plain(result)
        self.conversation.insert_message_at_end(result_formatted, msg_type="user")

        # Log if autolog is enabled
        if self.autolog:
            self.log(questiontag, "v1")


    def set_log_dir(self, log_dir: str) -> None:
        """Set the log directory for conversation logging.

        Args:
            log_dir: Root directory path for logging conversations
        """
        self.log_dir = log_dir

    def log(self, tag, version) -> None:
        """Log the current conversation state to a JSON file.

        Raises:
            ValueError: If log_dir is not set
        """
        if not self.log_dir:
            raise ValueError("log_dir must be set before logging")

        self.conversation.log(self.log_dir, self.db.name, self.model, tag, version)
