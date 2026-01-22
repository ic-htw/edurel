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