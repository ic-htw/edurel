from copy import deepcopy
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from edurel.syntax.er_ast import ERAstFactory, ERSchema, validate_ast
from edurel.syntax.er_yaml_schema import schema
from edurel.translation.er_trans import (
    ERSchemaTranslationBuilder,
    ERSchemaTranslationVisitor,
    YamlTranslationBuilder,
    RelAstTranslationBuilder,
    MermaidTranslationBuilder,
)
from edurel.utils.mermaid import display_mermaid_diagram as display_mermaid_diagram_util, save_mermaid_png
from edurel.utils.md import display_md, md_plain, md_yaml, md_sql
from edurel.utils.misc import save_text_to_file
from edurel.utils.yaml import parse_yaml


class ERSchemaMan:
    def __init__(self, yaml_str: Optional[str] = None, er_ast: Optional[ERSchema] = None):
        if yaml_str is None and er_ast is None:
            raise ValueError("Either yaml_str or er_ast must be provided")
        if yaml_str is not None and er_ast is not None:
            raise ValueError("Cannot provide both yaml_str and er_ast")
        if yaml_str is not None:
            yaml_dict = parse_yaml(yaml_str, schema)
            self.ast = ERAstFactory.create_schema(yaml_dict)
            validate_ast(self.ast)
        else:
            self.ast = deepcopy(er_ast)

    @classmethod
    def fromStr(cls, yaml_str: str) -> "ERSchemaMan":
        return cls(yaml_str)

    @classmethod
    def fromFile(cls, file_path: str) -> "ERSchemaMan":
        yaml_str = Path(file_path).read_text(encoding="utf-8")
        return cls(yaml_str)

    @classmethod
    def fromURL(cls, url: str) -> "ERSchemaMan":
        with urlopen(url) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            yaml_str = response.read().decode(encoding)
        return cls(yaml_str)

    @classmethod
    def fromAST(cls, er_ast: ERSchema) -> "ERSchemaMan":
        return cls(er_ast=er_ast)

    # HELPER
    def _translate(
        self,
        builder: ERSchemaTranslationBuilder,
        visitor_class: type[ERSchemaTranslationVisitor] = ERSchemaTranslationVisitor,
    ) -> str:
        visitor = visitor_class(builder)
        visitor.visit(self.ast)
        return builder.build()

    # AST
    def get_ast(self) -> ERSchema:
        return self.ast
    def display_ast(self) -> None:
        display_md(md_plain(str(self.ast)))

    # YAML
    def get_yaml(self) -> str:
        return self._translate(YamlTranslationBuilder(), ERSchemaTranslationVisitor)
    def display_yaml(self) -> None:
        display_md(md_yaml(self.get_yaml()))
    def save_yaml(self, output_path: str, overwrite: bool = False) -> None:
        save_text_to_file(self.get_yaml(), output_path, overwrite=overwrite)

    # REL
    def get_rel(self) -> str:
        return self._translate(RelAstTranslationBuilder(), ERSchemaTranslationVisitor)
    def display_rel(self) -> None:
        display_md(md_plain(str(self.get_rel())))
    def save_rel(self, output_path: str, overwrite: bool = False) -> None:
        save_text_to_file(str(self.get_rel()), output_path, overwrite=overwrite)

    # MERMAID
    def get_mermaid_code(self, direction: str = "TB") -> str:
        return self._translate(
            MermaidTranslationBuilder(direction=direction),
            ERSchemaTranslationVisitor,
        )
    def display_mermaid_code(self, direction: str = "TB") -> None:
        display_md(md_plain(self.get_mermaid_code(direction=direction)))
    def save_mermaid_code(self, output_path: str, direction: str = "TB", overwrite: bool = False) -> None:
        save_text_to_file(self.get_mermaid_code(direction=direction), output_path, overwrite=overwrite)
    def display_mermaid_diagram(self, direction="TB", width="100%", height="500px") -> None:
        mermaid_code = self.get_mermaid_code(direction=direction)
        display_mermaid_diagram_util(mermaid_code, width=width, height=height)
    def save_mermaid_diagram(
        self,
        output_path: str,
        direction: str = "TB",
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: float = 1.0,
        overwrite: bool = False
    ) -> None:
        file_path = Path(output_path)
        if not overwrite and file_path.exists():
            display_md(md_plain(f"File {output_path} already exists. Use overwrite=True to overwrite."))
            return
        mermaid_code = self.get_mermaid_code(direction=direction)
        save_mermaid_png(mermaid_code, output_path, width=width, height=height, scale=scale)    
    
