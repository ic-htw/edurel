# write a python class for viewing logs
- put the code in logviewer.py in utils folder
- the classname should be LogViewer
## init parameters of class
- log_dir: path, start of 4-level file hierarchy for log files
## instructions
- only fourth level contains entries (json files)
- each json file contains a list of objects with attributes "type" and "contents"
- file names are given by timestamps of the form yyyy_mm_dd___HH_MM_SS.json
- provide methods set_l1_filter, set_l2_filter, set_l3_filter, set_l4_filter
  - parameter: list of dir names or *
- provide a method read_log, that uses dir filters to read log files
  - optionnal parameter: list of timestamps of form yyyy_mm_dd___HH_MM_SS
  - if none read file with newest timestamp.json only
  - otherwise files with given timestamps
- log files should be stored internally by a dict 
  - key: dir path from l1 to l4 
  - entry: list of json dicts corresponding to read files
- provide a method display that outputs one markdown containg a concatenation of stored log entries
- start with a header1 presenting the dir path from l1 to l4 
- then all entries under that path
- enumerate all object within each log file 

