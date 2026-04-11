from textwrap import dedent

from langchain_core.language_models import BaseChatModel
from edurel.utils.misc import md_sql, md_yaml
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
        prompt = dedent(f"""
        The following tables are given
        {md_yaml(rel_yaml)}
        Future request will be based on this schema.
        """)
        self.insert_message_at_end(prompt)

        self.is_schema_set = True

    def set_initial_data(self, data_sql: str):
        if not self.is_schema_set:
            raise Exception("Database schema not set. Please call set_database_schema() with a valid YAML schema description before generating data.")
        prompt = dedent(f"""
        The following data is given 
        {md_sql(data_sql)}
        Don't repeat this data in future requests.
        """)
        self.insert_message_at_end(prompt)

        self.is_schema_set = True
    
    def datagen(self, model: BaseChatModel, no_of_records_per_table: int = 5, exclude_tables: List[str] = []) -> str:
        if not self.is_schema_set:
            raise Exception("Database schema not set. Please call set_database_schema() with a valid YAML schema description before generating data.")
        exclude_tables_str = ", ".join([f"'{table}'" for table in exclude_tables])
        prompt = dedent(f"""
        Don't repeat already created data.
        Create at least {no_of_records_per_table} insert statements for each table except for {exclude_tables_str}.
        """)
        response = self.call_llm(model, prompt)
        return response
