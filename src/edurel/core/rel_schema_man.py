from copy import deepcopy
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

from edurel.syntax.rel_ast import RelAstFactory, RelSchema, validate_ast, enrich_ast
from edurel.syntax.rel_yaml_schema import schema
from edurel.translation.rel_trans import (
    MermaidTranslationBuilder,
    RelSchemaTranslationBuilder,
    RelSchemaTranslationVisitor,
    RelSchemaLevelTranslationVisitor,
    SqlInlineTranslationBuilder,
    SqlTranslationBuilder,
    StructureTranslationBuilder,
    YamlTranslationBuilder,
)
from edurel.utils.mermaid import display_mermaid_diagram as display_mermaid_diagram_util, save_mermaid_png
from edurel.utils.md import display_md, md_plain, md_yaml, md_sql
from edurel.utils.misc import save_text_to_file
from edurel.utils.yaml import parse_yaml


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
    def fromStr(cls, yaml_str: str) -> "RelSchemaMan":
        return cls(yaml_str)

    @classmethod
    def fromFile(cls, file_path: str) -> "RelSchemaMan":
        yaml_str = Path(file_path).read_text(encoding="utf-8")
        return cls(yaml_str)

    @classmethod
    def fromURL(cls, url: str) -> "RelSchemaMan":
        with urlopen(url) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            yaml_str = response.read().decode(encoding)
        return cls(yaml_str)

    @classmethod
    def fromAST(cls, rel_ast: RelSchema) -> "RelSchemaMan":
        return cls(rel_ast=rel_ast)

    # HELPER
    def _translate(
        self,
        builder: RelSchemaTranslationBuilder,
        visitor_class: type[RelSchemaTranslationVisitor] = RelSchemaTranslationVisitor,
    ) -> str:
        visitor = visitor_class(builder)
        visitor.visit(self.ast)
        return builder.build()

    # AST
    def get_ast(self) -> RelSchema:
        return self.ast
    def display_ast(self) -> None:
        display_md(md_plain(f"{str(self.ast)}"))

    # YAML
    def get_yaml(self) -> str:
        return self._translate(YamlTranslationBuilder(), RelSchemaTranslationVisitor)
    def display_yaml(self) -> None:
        display_md(md_yaml(self.get_yaml()))
    def save_yaml(self, output_path: str, overwrite: bool = False) -> None:
        save_text_to_file(self.get_yaml(), output_path, overwrite=overwrite)

    # SQL
    def get_sql(self) -> str:
        return self._translate(SqlTranslationBuilder(), RelSchemaTranslationVisitor)
    def display_sql(self) -> None:
        display_md(md_sql(self.get_sql()))
    def get_sql_inline(self) -> str:
        enrich_ast(self.ast)
        return self._translate(SqlInlineTranslationBuilder(), RelSchemaLevelTranslationVisitor)
    def display_sql_inline(self) -> None:
        display_md(md_sql(self.get_sql_inline()))
    def save_sql(self, output_path: str, overwrite: bool = False) -> None:
        save_text_to_file(self.get_sql(), output_path, overwrite=overwrite)
    def save_sql_inline(self, output_path: str, overwrite: bool = False) -> None:
        save_text_to_file(self.get_sql_inline(), output_path, overwrite=overwrite)

    # MERMAID
    def get_mermaid_code(self, direction: str = "TB") -> str:
        return self._translate(
            MermaidTranslationBuilder(direction=direction),
            RelSchemaTranslationVisitor,
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
    
    # STRUCTURE
    def get_structure(self) -> str:
        return self._translate(StructureTranslationBuilder(), RelSchemaTranslationVisitor)
    def display_structure(self) -> None:
        display_md(md_plain(self.get_structure()))
