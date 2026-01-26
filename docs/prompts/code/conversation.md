# write a python class for chats with a large language model
- put the code in chat.py in utils folder
- the classname should be Conversation
- use langchain and langraph
- only use api version 1.0 or newer
## init parameters of class
- model: a langchain base model
## implementation
- provide a method to set a system prompt
- provide a method to add a new user prompt
- keep track of conversation history
- provide a method to show complete conversation chain, indicate type of individual elements (system, user , ai)
- provide a method to select a single element from the conversation chain
- provide a method to select a a set of didicated elements from the conversation chain
- provide a method to manipulate the conversation chain

# extend class Conversation by a new method to log conversations
- the name of the method should be log_conversation
- conversations should be logged in a file hierarchie starting at log_dir
## parameters
- log_dir - start of file hierarchy to store conversation files
- l1 - name of sub directory on first level 
- l2 - name of sub directory on second level 
- l3 - name of sub directory on third level 
- l4 - name of sub directory on fourth level 
## instructions
- conversations should be stored as json
- conversations should only be stored on the fourth level 
- the file names should be timestamps of the form yyyy_mm_dd___HH_MM_SS.json
- if a directory does not exist, it should be created

# rewrite class Conversation
- provide an enum for clients with values ANTHROPIC, STATS, OLLAMA, OPENAI
- provide a dict that turn client enum values into clients
- turn the LLM name constants into an enum
- provide a dict that turn llm name enum values into string values
- provide a factory method for class Conversation that has the following parameters:
  - client enum value
  - llm name enum value