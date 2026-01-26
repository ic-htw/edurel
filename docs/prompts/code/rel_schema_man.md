- turn function yaml_to_yaml and all its helpers from yaml_utils.py into a method of class SMan in sman.py


- add a method to class SMan the turns the init paramter yaml_str into a dict and stores that in an instance variable yaml_base_dict
- change yaml_to_yaml to use this yaml_base_dict


- turn function yaml_remove_tags from yaml_utils.py into a method of class SMan in sman.py

- add an instance variable yaml_dict to class SMan
- rename method yaml_to_yaml into reduce
- rewrite reduce such that it assigns its result to yaml_dict and has no return value

- add a method yaml to class SMan that return yaml_dict as string

- change class SMan
  - remove instance variable yaml_base
  - rename yaml_remove_tags into remove_tags
  - in __init__ store parsed yaml_str in yaml_base_dict and a copy in yaml_dict
  - methods reduce and remove_tags should modify yaml_dict in place
  - adapt method yaml
  - add method yaml_base return yaml_base_dict as string

- turn function yaml_to_mermaid in yaml_utils.py into a method of class SMan 
- rename it to mermaid
- it should use yaml_dict to generate mermaid code

- turn function schema_mermaid_png in mermaid.py into a method of class SMan 
- rename it to save_mermaid_png
- it should use method mermaid from this class to generate the png file

  each table contains "foreign_keys" that have to be extended

  - the spec to add fks looks as follows
    - it is a string where each line descibes an fk in the following way
    - name of source table | source col1, source col 2, ... |-->| target table | target col 1, target col 2 ...
    - strip white spaces
    - check structure of spec

  - the fks have to be added to foreign_keys in the table with tablename "source table"

change method add_fks in class RelSchemaMan see rel_schema_man.py
- change spec to a file path to a yaml file with the following structure
  ```yaml
  foreign_keys:
  - OrgUnit|Head|-->|Employee|EID
  - OrgUnit|SuperUnit|-->|OrgUnit|OEID
  ```
- each element of list foreign_keys contains a foreign key spec as before

change method remove_tags in class RelSchemaMan see rel_schema_man.py
- change omit_tags to a file path to a yaml file with the following structure
  ```yaml
  omit_tags:
  - nullable
  - fkname
  ```
- rename omit_tags to spec_file_path
- list omit_tags can be used as before

change method transform in class RelSchemaMan see rel_schema_man.py
- change spec to a file path to a yaml file with the following structure
  ```yaml
  transformation_steps:
  - step1
  - step3
  - step3
  ```
- each element of list transformation_steps contains a transformation as before
