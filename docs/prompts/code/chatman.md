# create a jupyter notebook widget for the for the conversation with a large language model
- put the code into file chatman.py in widgets folder
- the new widget class should be called ChatMan
- the class should provide methods to
  - track conversation history
  - set/replace system prompt
  - manipulate the conversation chain
    - replace messages
    - delete message
    - add messages
  - export the complete conversation chain
  - import the complete conversation chain

## init parameters of class
- chat: an instance of class LLMChat see utils/llmchat.py
- chat_path: an optional path to a folder where chats should be stored

## implementation
- the widget should use a suitable set of labels, buttons, and textboxes
- the first textbox should contain the system message
- it should be followed by a list of textboxes for the conversation chain
  - each textbox of conversation chain the should contain one message of the chat 
- left to each textbox should be a lable indicating the type of message 
  - SystemMessage (S)
  - HumanMessage (U)
  - AIMessage (A)
- right to each textbox should be a list of buttons for deletion an replacement
- the name of the file for the conversation chain should be provided in a textbox

- add a button to class ChatMan to delete the complete conversation
- enlarge the height of the textboxes