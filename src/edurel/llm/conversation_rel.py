from textwrap import dedent

from langchain_core.language_models import BaseChatModel
from edurel.utils.md import md_sql, md_yaml
from typing import List
from edurel.llm.conversation_base import Conversation

# ---------------------------------------------------------------------------------------------
# class DataGenConversation:
# ---------------------------------------------------------------------------------------------
class DataGenConversation(Conversation):
    def __init__(self):
        super().__init__()
        self.is_schema_set = False

        system_prompt = dedent("""
        You are a helpful assistant for generating synthetic data for SQL tables.
        You will be given a YAML description of the tables and their relationships, 
        as well as some existing data in SQL insert statement format.
        Your task is to generate additional SQL insert statements to create more synthetic data 
        for the tables, while respecting the relationships and constraints described in the YAML.
        """)

        self.set_system_prompt(system_prompt)

    def set_database_schema(self, rel_yaml: str):
        prompt = []
        prompt.append("The following tables are given:")
        prompt.append(md_yaml(rel_yaml))
        prompt.append("Future request will be based on this schema.")
        self.insert_message_at_end("\n".join(prompt))

        self.is_schema_set = True

    def set_already_existing_data(self, data_sql: str) -> None:
        if not self.is_schema_set:
            raise Exception("Database schema not set. Please call set_database_schema().")
        prompt = []
        prompt.append("The following data is already given:")
        prompt.append(md_sql(data_sql))
        prompt.append("Don't repeat this data in future requests.")
        self.insert_message_at_end("\n".join(prompt))
    
    def insert_datagen_message(self, no_of_records_per_table: int = 5, exclude_tables: List[str] = []) -> None:
        if not self.is_schema_set:
            raise Exception("Database schema not set. Please call set_database_schema().")
        prompt = []
        prompt.append(
            dedent(f"""
            Create at least {no_of_records_per_table} insert statements for each table.
            Don't repeat already created data.
            """)
        )
        
        if exclude_tables:
            exclude_tables_str = ", ".join([f"'{table}'" for table in exclude_tables])
            prompt.append(f"Don'create insert statements for the following tables: {exclude_tables_str}.")

        self.insert_message_at_end("\n".join(prompt))

# ---------------------------------------------------------------------------------------------
# class SQLGenConversation:
# ---------------------------------------------------------------------------------------------
class SQLGenConversation(Conversation):
    def __init__(self):
        super().__init__()
        self.is_schema_set = False

        system_prompt = dedent("""
        You are an expert SQL query generator. 
        Convert natural language questions into valid SQL queries. 
        """)

        self.set_system_prompt(system_prompt)

    def set_database_schema(self, db_schema: str):
        prompt = []
        prompt.append("The following database schema is given:")
        prompt.append(db_schema)
        prompt.append("\nFuture request will be based on this schema.")
        self.insert_message_at_end("\n".join(prompt))

        self.is_schema_set = True

    def insert_question_message(self, question: str, dbkind: str = "duckdb") -> None:
        if not self.is_schema_set:
            raise Exception("Database schema not set. Please call set_database_schema().")
        
        prompt = []
        prompt.append("The user's question is:")
        prompt.append(question)
        prompt.append(f"Turn this question into a valid {dbkind} SQL query based on the given database schema.")
        prompt.append("Return the SQL query only, without any explanation or additional text.")
        self.insert_message_at_end("\n".join(prompt))
    
