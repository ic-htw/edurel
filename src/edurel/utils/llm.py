# ---------------------------------------------------------------------------------------------
# Import / Config
# ---------------------------------------------------------------------------------------------
import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama
  
from langchain_core.prompts.chat import ChatPromptTemplate

# ---------------------------------------------------------------------------------------------
# Chat Clients
# ---------------------------------------------------------------------------------------------
def anthropic_c(model, timeout=60, max_retries=0, temperature=0):
    return ChatAnthropic(
        model=model,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )

def stats_c(model, timeout=60, max_retries=0, temperature=0):
    return ChatOpenAI(
        model=model,
        api_key=os.getenv("LLM_STATS_API_KEY"),
        base_url="https://api.zeroeval.com/v1",
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
    )

def ollama_c(model, timeout=60, max_retries=0, temperature=0):
    return ChatOllama(
        model=model,
        # validate_model_on_init=True,
        timeout=timeout,
        max_retries=max_retries,
        temperature=temperature,
        base_url=os.getenv("OLLAMA_API_URL"),
        client_kwargs={"verify": False},
    )

def openai_c(model, timeout=60, max_retries=0, temperature=0):
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
GEMINI25PRO ="gemini-2.5-pro"
GEMINI3PRO ="gemini-3-pro-preview"
GLM46 = "glm-4.6"
GPT41MINI = "gpt-4.1-mini-2025-04-14"
GPT5 = "gpt-5-2025-08-07"
GPT5MINI = "gpt-5-mini-2025-08-07"
GROK4 = "grok-4"
KIMIK2 = "kimi-k2-0905"
OPUS41 = "claude-opus-4-1-20250805"
SONNET4 ="claude-sonnet-4-20250514"
SONNET45 ="claude-sonnet-4-5-20250929"



# ---------------------------------------------------------------------------------------------
# Text to SQL
# ---------------------------------------------------------------------------------------------
def chat_text_to_sql(chatmodel, schema, question):
    def clean_reponse(r):
        r = r.strip()
        r = r.strip().replace("sql", "").replace("SQL", "")
        r = r.replace("```", "")
        return r

    system_prompt = """
    You are an expert SQL query generator. 
    Convert natural language questions into valid SQL queries.
    use postgres syntax.
    """

    user_prompt = """
    Database schema:
    {schema}
    User request: 
    {question}
    Return only the SQL query. Do not explain.
    """
    sql_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    chain = sql_prompt | chatmodel

    response = chain.invoke({
        "schema": schema,
        "question": question
    })

    query = clean_reponse(response.content)
    return query

# ---------------------------------------------------------------------------------------------
# Explain Schema
# ---------------------------------------------------------------------------------------------
def chat_explain_schema(chatmodel, schema, lang="English"):
    system_prompt = """
    You are an  SQL expert. 
    """

    user_prompt = """
    Database schema:
    {schema}
    User request: 
    Explain the database schema in detail in {lang}.
    Return the explanation only. Do not mention the schema.
    """
    sql_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    chain = sql_prompt | chatmodel

    response = chain.invoke({
        "schema": schema,
        "lang": lang
    })

    return response.content

# ---------------------------------------------------------------------------------------------
# Explain query
# ---------------------------------------------------------------------------------------------
def chat_explain_query(chatmodel, schema, query, lang="English"):
    system_prompt = """
    You are an  SQL expert. 
    """

    user_prompt = """
    Database schema:
    {schema}
    Query
    {query}
    User request: 
    Explain the query in detail in {lang}.
    Return the explanation only. Do not mention the schema.
    """
    sql_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    chain = sql_prompt | chatmodel

    response = chain.invoke({
        "schema": schema,
        "query": query,
        "lang": lang
    })

    return response.content
