from copy import deepcopy
from pathlib import Path
from typing import List, Optional

from edurel.utils.misc import display_md, md_plain
from edurel.utils.yaml import parse_yaml
from edurel.syntax.rel_yaml_schema import schema
from edurel.syntax.rel_ast import RelAstFactory, RelSchema, validate_ast

class RelSchemaMan:
    def __init__(self, yaml_str: Optional[str] = None, rel_ast: Optional[RelSchema] = None):
        if yaml_str is None and rel_ast is None:
            raise ValueError("Either yaml_str or rel_ast must be provided")
        if yaml_str is not None and rel_ast is not None:
            raise ValueError("Cannot provide both yaml_str and rel_ast")
        if yaml_str is not None:
            yaml_dict = parse_yaml(yaml_str, schema)
            self.ast = RelAstFactory.create_schema(yaml_dict)
            validate_ast(self.ast)
        else:
            self.ast = deepcopy(rel_ast)

    @classmethod
    def fromStr(cls, yaml_str: str) -> 'RelSchemaMan':
        return cls(yaml_str)

    @classmethod
    def fromFile(cls, file_path: str) -> 'RelSchemaMan':
        yaml_str = Path(file_path).read_text(encoding="utf-8")
        return cls(yaml_str)

    @classmethod
    def fromAST(cls, rel_ast: RelSchema) -> 'RelSchemaMan':
         return cls(rel_ast=rel_ast)

    def get_ast(self) -> RelSchema:
        return self.ast
    
    def display_ast(self) -> None:
        display_md(md_plain(f"{str(self.ast)}"))
