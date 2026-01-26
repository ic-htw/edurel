# write a python class for for a SQL agent
- put the code in sql_agent.py in utils folder
- the classname should be SQLAgent
- use classes Conversation, Db, QuestionMan, RelSchemaMan from utils folder
## init parameters of class
- db: object of class Db
- client: value of enum Client
- llm_name: value of enum LLMName
- system_prompt: optional, of type str
- reduce_spec: optional, of type str
- fk_spec: optional, of type str
- rem_tags_spec: optional, of type List[str]
- log_dir: optional, path to root directory for the log file hierarchy
- autolog: optional, bool
## __init __
- create an instance of class RelSchemaMan
  - initialize with db schema
  - apply all yaml transforms given by specs
- create an instance of class Conversation
  - set system prompt
  - if none is given use: You are an expert SQL query generator. Convert natural language questions into valid SQL queries. Use duckdb syntax.
  - insert schema at end, use method yaml of RelSchemaMan
  - check if log_dir is set when auto_log=True
## methods
- provide a method text2sql 
  - parameter question
  - execute add_user_message 
  - if result contains "err:" insert result as  ai message at end of conversation, stop execution
  - otherwise extract sql code using function sql_extract from misc.py
  - execute sql code in db using method eval_nx
  - insert result at end of conversation tagged as markdown plaintext
  - log execution if autolog=True
- provide a method set_log_dir
- provide a method log, that logs the current state of the conversation