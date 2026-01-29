"""SQL Agent for natural language to SQL query generation."""

from typing import Optional, List
from datetime import datetime
from edurel.utils.duckdb import Db
from edurel.utils.conversation import Conversation, Client, LLMName
from edurel.utils.rel_schema_man import RelSchemaMan
from edurel.utils.misc import sql_extract, md_plain, md_yaml

_system_prompt = """
You are an expert entity-relationship (ER) modeling assistant. 
Your task is to design ER diagrams based on their natural language descriptions. 
The ER diagrams should conform to the following yaml schema: 
```yaml
entities:
# only atomic keys and attributes
# use associative_entities if composite keys are needed
- entityname: E1
  key: K1 
  attributes:
  - attributename: A11
    type: INTEGER
  - attributename: A12
    type: TEXT
  - attributename: A13
    type: DATE
  - attributename: A14
    type: DECIMAL
- entityname: E2
  key: K2
  attributes:
  - attributename: A21
    type: INTEGER
  - attributename: A22
    type: TEXT
  - attributename: A23
    type: DATE
  - attributename: A24
    type: DECIMAL

associative_entities:
# identification alternatives
# 1. just atomic key
# 2. identified by other entities (only with cardinality ONE)
# 3. combination of both
# if roles are omitted in associations, default roles are used (E1, E2, ...)
# Associations are entities and relationships at the same time
- associationname: AE1
  associations:
  - targetentity: E1
    role: Role1
    cardinality: ONE
  - targetentity: E2
    role: Role2 
    cardinality: ONE
  - targetentity: E3
    role: Role2 
    cardinality: MANY
  key: KAE1 #
  identified_by:
  - targetentity: E1
    cardinality: ONE
  - targetentity: E2
    cardinality: ONE
  attributes:
  - attributename: AEA1
    type: INTEGER
  - attributename: AEA2
    type: TEXT
  - attributename: AEA3
    type: DATE
  - attributename: AEA4
    type: DECIMAL

relationships:
# if roles are omitted in associations, default roles are used (E1, E2, ...)
# all relationships are binary
# cardinality values: ONE, MANY, OPTIONAL_ONE, OPTIONAL_MANY
- relationshipname: R1
  entities:
  - entityname: E1
    role: Role1
  - entityname: E2
    role: Role2
  cardinality:
    Role1: MANY
    Role2: ONE
  attributes:
  - attributename: RA1
    type: INTEGER
  - attributename: RA2
    type: TEXT
  - attributename: RA3
    type: DATE
  - attributename: RA4
    type: DECIMAL    

inheritances:
# only single inheritance is supported
- superentity: E1
  subentities:
  - E1A
  - E1B

valuelists:
# each valuelist is an entity with the following attributes:
# ID: INTEGER
# Description: TEXT
# IsValid: BOOLEAN
# SortOrder: INTEGER
# valulists will be transformed into tables in the relational schema
# each row in that table represents one value in the valuelist
- valuelistname: VL1
- valuelistname: VL2
```
"""

class ERAgent:

    def __init__(
        self,
        client: Client,
        llm_name: LLMName,
        domain: str,
        system_prompt: Optional[str] = None,
        db: Optional[Db] = None,
        log_dir: Optional[str] = None,
    ):
        """Initialize SQLAgent with database, LLM, and optional transformations.

        Args:
            client: LLM client enum value (e.g., Client.ANTHROPIC)
            llm_name: LLM model name enum value (e.g., LLMName.SONNET45)
            system_prompt: Optional custom system prompt for the LLM
            db: Database to create relational schema und insert test data
            log_dir: Optional root directory for logging conversations
        """
        self.model = llm_name.name
        self.domain = domain
        self.db = db
        self.log_dir = log_dir

        # Create Conversation instance
        self.conversation = Conversation.create(
            client=client,
            llm_name=llm_name
        )

        # Set system prompt
        if system_prompt is None:
            system_prompt = _system_prompt

        self.conversation.set_system_prompt(system_prompt)

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

        self.conversation.log(self.log_dir, self.domain, self.model, tag, version)

    def prune_conversation(self, from_index: int) -> None:
        self.conversation.delete_slice(from_index)
        
    def text2er(self, descriptiontag: str, description: str, version: str = "v1", autolog: bool = False) -> None:
        """Convert natural language description to ER diagram.

        Args:
            descriptiontag: Tag or identifier for the description
            description: Natural language description to convert to ER diagram
        """

        if autolog and not self.log_dir:
            raise ValueError("log_dir must be set when autolog is True")
        
        ok = True

        # Get LLM response
        response = self.conversation.add_user_message(description)

        # Check for error in response
        if "err:" in response:
            # Insert error as AI message and stop
            self.conversation.insert_message_at_end(response, msg_type="ai")
            ok = False

       # Log if autolog is enabled
        if autolog:
            self.log(descriptiontag, version)

