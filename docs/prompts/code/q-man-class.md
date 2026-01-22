# write a python class for for the management of question sets
- put the code in qman.py in utils folder
- the classname should be QMan
## init parameters of class
- qpath: path to the file containing questions
## structure of file contents
- empty lines can appear throughout the file
- first non-empty line starts with "---db:" followed by any number of white space and a database name
- after that a repetion of questions follows
- each question starts with "---tag:" followed by any number of white space and the text of the tag
- after that the question is given in an arbitrary number of lines
- a question ends if either a new tag line appears or at end of file
- an example file is given in questions/company_en.txt
## instructions
- store all questions in order and under their corresponding tags
- provide a method to access questions by tags
- provide a method to access questions by index, list of indexes, slices and list of slices
- index-based method should return lists of tuples where first element in tuple is tag and second is question
- generate tests based on file questions/company_en.txt

