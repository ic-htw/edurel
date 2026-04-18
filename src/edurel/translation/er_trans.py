from abc import ABC, abstractmethod
import re

from edurel.syntax.er_ast import (
    Association,
    AssociativeEntity,
    Attribute,
    Entity,
    ERSchema,
    GlobalKey,
    Identification,
    Inheritance,
    ManyToOneEntity,
    Relationship,
    RelationshipEntity,
    ValueList,
)
from edurel.syntax.rel_ast import Column, DataList, ForeignKey, RelSchema, Table


class ERSchemaTranslationBuilder(ABC):
    @abstractmethod
    def start_schema(self, er_schema: ERSchema) -> None:
        pass

    @abstractmethod
    def end_schema(self, er_schema: ERSchema) -> None:
        pass

    @abstractmethod
    def start_entity(self, entity: Entity) -> None:
        pass

    @abstractmethod
    def add_entity_key(self, entity: Entity) -> None:
        pass

    @abstractmethod
    def add_entity_attribute(self, entity: Entity, attribute: Attribute) -> None:
        pass

    @abstractmethod
    def end_entity(self, entity: Entity) -> None:
        pass

    @abstractmethod
    def start_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        pass

    @abstractmethod
    def start_identification(self, identification: Identification) -> None:
        pass

    @abstractmethod
    def add_global_key(
        self, identification: Identification, global_key: GlobalKey
    ) -> None:
        pass

    @abstractmethod
    def end_identification(self, identification: Identification) -> None:
        pass

    @abstractmethod
    def add_association(
        self, associative_entity: AssociativeEntity, association: Association
    ) -> None:
        pass

    @abstractmethod
    def add_associative_entity_attribute(
        self, associative_entity: AssociativeEntity, attribute: Attribute
    ) -> None:
        pass

    @abstractmethod
    def end_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        pass

    @abstractmethod
    def start_relationship(self, relationship: Relationship) -> None:
        pass

    @abstractmethod
    def add_relationship_entity(
        self, relationship: Relationship, entity: RelationshipEntity
    ) -> None:
        pass

    @abstractmethod
    def add_relationship_attribute(
        self, relationship: Relationship, attribute: Attribute
    ) -> None:
        pass

    @abstractmethod
    def end_relationship(self, relationship: Relationship) -> None:
        pass

    @abstractmethod
    def add_inheritance(self, inheritance: Inheritance) -> None:
        pass

    @abstractmethod
    def start_valuelist(self, valuelist: ValueList) -> None:
        pass

    @abstractmethod
    def add_many_to_one_entity(
        self, valuelist: ValueList, entity: ManyToOneEntity
    ) -> None:
        pass

    @abstractmethod
    def end_valuelist(self, valuelist: ValueList) -> None:
        pass

    @abstractmethod
    def build(self) -> str:
        pass


class ERSchemaTranslationVisitor:
    def __init__(self, builder: ERSchemaTranslationBuilder):
        self.builder = builder

    def visit(
        self,
        node: ERSchema
        | Entity
        | AssociativeEntity
        | Identification
        | Relationship
        | Inheritance
        | ValueList,
    ) -> None:
        visit_method = getattr(self, f"visit_{type(node).__name__}")
        visit_method(node)

    def visit_ERSchema(self, er_schema: ERSchema) -> None:
        self.builder.start_schema(er_schema)
        for entity in er_schema.entities:
            self.visit(entity)
        for associative_entity in er_schema.associative_entities:
            self.visit(associative_entity)
        for relationship in er_schema.relationships:
            self.visit(relationship)
        for inheritance in er_schema.inheritances:
            self.visit(inheritance)
        for valuelist in er_schema.valuelists:
            self.visit(valuelist)
        self.builder.end_schema(er_schema)

    def visit_Entity(self, entity: Entity) -> None:
        self.builder.start_entity(entity)
        if entity.key is not None:
            self.builder.add_entity_key(entity)
        for attribute in entity.attributes:
            self.builder.add_entity_attribute(entity, attribute)
        self.builder.end_entity(entity)

    def visit_AssociativeEntity(self, associative_entity: AssociativeEntity) -> None:
        self.builder.start_associative_entity(associative_entity)
        if associative_entity.identification is not None:
            self.visit(associative_entity.identification)
        for association in associative_entity.associations:
            self.builder.add_association(associative_entity, association)
        for attribute in associative_entity.attributes:
            self.builder.add_associative_entity_attribute(associative_entity, attribute)
        self.builder.end_associative_entity(associative_entity)

    def visit_Identification(self, identification: Identification) -> None:
        self.builder.start_identification(identification)
        for global_key in identification.global_keys:
            self.builder.add_global_key(identification, global_key)
        self.builder.end_identification(identification)

    def visit_Relationship(self, relationship: Relationship) -> None:
        self.builder.start_relationship(relationship)
        for entity in relationship.entities:
            self.builder.add_relationship_entity(relationship, entity)
        for attribute in relationship.attributes:
            self.builder.add_relationship_attribute(relationship, attribute)
        self.builder.end_relationship(relationship)

    def visit_Inheritance(self, inheritance: Inheritance) -> None:
        self.builder.add_inheritance(inheritance)

    def visit_ValueList(self, valuelist: ValueList) -> None:
        self.builder.start_valuelist(valuelist)
        for entity in valuelist.many_to_one_from_entities:
            self.builder.add_many_to_one_entity(valuelist, entity)
        self.builder.end_valuelist(valuelist)


def _yaml_scalar(value: str | bool) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value == "" or value.lower() in {"true", "false", "null", "~"}:
        return "'" + value.replace("'", "''") + "'"
    if re.fullmatch(r"[A-Za-z0-9_(), .-]+", value):
        return value
    return "'" + value.replace("'", "''") + "'"


def _strip_attribute_type_size(attribute_type: str) -> str:
    return re.sub(r"\s*\(.*\)$", "", attribute_type).strip()


def _member_type(attribute_type: str | None, default: str = "INTEGER") -> str:
    if attribute_type is None:
        return default
    stripped_type = _strip_attribute_type_size(attribute_type)
    return stripped_type or default


def _mermaid_cardinality(cardinality: str | None) -> str:
    if cardinality == "ONE":
        return "1"
    if cardinality == "OPTIONAL_ONE":
        return "0..1"
    if cardinality in {"MANY", "OPTIONAL_MANY"}:
        return "0..*"
    return "1"


def _mermaid_text(value: str) -> str:
    return value.replace('"', '\\"')


class YamlTranslationBuilder(ERSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.entities: list[dict] = []
        self.associative_entities: list[dict] = []
        self.relationships: list[dict] = []
        self.inheritances: list[dict] = []
        self.valuelists: list[dict] = []
        self.current_entity: dict | None = None
        self.current_associative_entity: dict | None = None
        self.current_identification: dict | None = None
        self.current_relationship: dict | None = None
        self.current_valuelist: dict | None = None

    def start_schema(self, er_schema: ERSchema) -> None:
        self.entities = []
        self.associative_entities = []
        self.relationships = []
        self.inheritances = []
        self.valuelists = []

    def end_schema(self, er_schema: ERSchema) -> None:
        return None

    def start_entity(self, entity: Entity) -> None:
        self.current_entity = {"entityname": entity.entityname}

    def add_entity_key(self, entity: Entity) -> None:
        assert self.current_entity is not None
        self.current_entity["key"] = entity.key
        if entity.keytype is not None:
            self.current_entity["keytype"] = entity.keytype

    def add_entity_attribute(self, entity: Entity, attribute: Attribute) -> None:
        assert self.current_entity is not None
        self.current_entity.setdefault("attributes", []).append(
            self._attribute_dict(attribute)
        )

    def end_entity(self, entity: Entity) -> None:
        assert self.current_entity is not None
        self.entities.append(self.current_entity)
        self.current_entity = None

    def start_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        self.current_associative_entity = {
            "associationname": associative_entity.associationname
        }

    def start_identification(self, identification: Identification) -> None:
        self.current_identification = {}
        if identification.localkey is not None:
            self.current_identification["localkey"] = identification.localkey
        if identification.keytype is not None:
            self.current_identification["keytype"] = identification.keytype

    def add_global_key(
        self, identification: Identification, global_key: GlobalKey
    ) -> None:
        assert self.current_identification is not None
        global_key_dict = {"targetentity": global_key.targetentity}
        if global_key.role is not None:
            global_key_dict["role"] = global_key.role
        self.current_identification.setdefault("global", []).append(global_key_dict)

    def end_identification(self, identification: Identification) -> None:
        assert self.current_associative_entity is not None
        assert self.current_identification is not None
        self.current_associative_entity["identification"] = self.current_identification
        self.current_identification = None

    def add_association(
        self, associative_entity: AssociativeEntity, association: Association
    ) -> None:
        assert self.current_associative_entity is not None
        association_dict = {"targetentity": association.targetentity}
        if association.role is not None:
            association_dict["role"] = association.role
        if association.cardinality is not None:
            association_dict["cardinality"] = association.cardinality
        self.current_associative_entity.setdefault("associations", []).append(
            association_dict
        )

    def add_associative_entity_attribute(
        self, associative_entity: AssociativeEntity, attribute: Attribute
    ) -> None:
        assert self.current_associative_entity is not None
        self.current_associative_entity.setdefault("attributes", []).append(
            self._attribute_dict(attribute)
        )

    def end_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        assert self.current_associative_entity is not None
        self.associative_entities.append(self.current_associative_entity)
        self.current_associative_entity = None

    def start_relationship(self, relationship: Relationship) -> None:
        self.current_relationship = {"relationshipname": relationship.relationshipname}

    def add_relationship_entity(
        self, relationship: Relationship, entity: RelationshipEntity
    ) -> None:
        assert self.current_relationship is not None
        relationship_entity_dict = {"targetentity": entity.entityname}
        if entity.role is not None:
            relationship_entity_dict["role"] = entity.role
        if entity.cardinality is not None:
            relationship_entity_dict["cardinality"] = entity.cardinality
        self.current_relationship.setdefault("entities", []).append(
            relationship_entity_dict
        )

    def add_relationship_attribute(
        self, relationship: Relationship, attribute: Attribute
    ) -> None:
        assert self.current_relationship is not None
        self.current_relationship.setdefault("attributes", []).append(
            self._attribute_dict(attribute)
        )

    def end_relationship(self, relationship: Relationship) -> None:
        assert self.current_relationship is not None
        self.relationships.append(self.current_relationship)
        self.current_relationship = None

    def add_inheritance(self, inheritance: Inheritance) -> None:
        inheritance_dict = {
            "superentity": inheritance.superentity,
            "subentities": list(inheritance.subentities),
        }
        if inheritance.implementation is not None:
            inheritance_dict["implementation"] = inheritance.implementation
        self.inheritances.append(inheritance_dict)

    def start_valuelist(self, valuelist: ValueList) -> None:
        self.current_valuelist = {
            "valuelistname": valuelist.valuelistname,
            "values": list(valuelist.values),
        }

    def add_many_to_one_entity(
        self, valuelist: ValueList, entity: ManyToOneEntity
    ) -> None:
        assert self.current_valuelist is not None
        self.current_valuelist.setdefault("many_to_one_from_entities", []).append(
            {"sourceentity": entity.entityname}
        )

    def end_valuelist(self, valuelist: ValueList) -> None:
        assert self.current_valuelist is not None
        self.valuelists.append(self.current_valuelist)
        self.current_valuelist = None

    def build(self) -> str:
        lines: list[str] = []

        if self.entities:
            lines.append("entities:")
            for entity in self.entities:
                lines.append(f"- entityname: {_yaml_scalar(entity['entityname'])}")
                if "key" in entity:
                    lines.append(f"  key: {_yaml_scalar(entity['key'])}")
                if "keytype" in entity:
                    lines.append(f"  keytype: {_yaml_scalar(entity['keytype'])}")
                self._append_attributes(lines, entity.get("attributes", []))

        if self.associative_entities:
            lines.append("associative_entities:")
            for associative_entity in self.associative_entities:
                lines.append(
                    f"- associationname: "
                    f"{_yaml_scalar(associative_entity['associationname'])}"
                )
                identification = associative_entity.get("identification")
                if identification is not None:
                    self._append_identification(lines, identification)
                associations = associative_entity.get("associations", [])
                if associations:
                    lines.append("  associations:")
                    for association in associations:
                        lines.append(
                            f"  - targetentity: "
                            f"{_yaml_scalar(association['targetentity'])}"
                        )
                        if "role" in association:
                            lines.append(f"    role: {_yaml_scalar(association['role'])}")
                        if "cardinality" in association:
                            lines.append(
                                "    cardinality: "
                                f"{_yaml_scalar(association['cardinality'])}"
                            )
                self._append_attributes(
                    lines, associative_entity.get("attributes", [])
                )

        if self.relationships:
            lines.append("relationships:")
            for relationship in self.relationships:
                lines.append(
                    f"- relationshipname: "
                    f"{_yaml_scalar(relationship['relationshipname'])}"
                )
                lines.append("  entities:")
                for entity in relationship["entities"]:
                    lines.append(
                        f"  - targetentity: {_yaml_scalar(entity['targetentity'])}"
                    )
                    if "role" in entity:
                        lines.append(f"    role: {_yaml_scalar(entity['role'])}")
                    if "cardinality" in entity:
                        lines.append(
                            f"    cardinality: {_yaml_scalar(entity['cardinality'])}"
                        )
                self._append_attributes(lines, relationship.get("attributes", []))

        if self.inheritances:
            lines.append("inheritances:")
            for inheritance in self.inheritances:
                lines.append(
                    f"- superentity: {_yaml_scalar(inheritance['superentity'])}"
                )
                lines.append("  subentities:")
                for subentity in inheritance["subentities"]:
                    lines.append(f"  - {_yaml_scalar(subentity)}")
                if "implementation" in inheritance:
                    lines.append(
                        "  implementation: "
                        f"{_yaml_scalar(inheritance['implementation'])}"
                    )

        if self.valuelists:
            lines.append("valuelists:")
            for valuelist in self.valuelists:
                lines.append(
                    f"- valuelistname: {_yaml_scalar(valuelist['valuelistname'])}"
                )
                lines.append("  values:")
                for value in valuelist["values"]:
                    lines.append(f"  - {_yaml_scalar(value)}")
                many_to_one_entities = valuelist.get("many_to_one_from_entities", [])
                if many_to_one_entities:
                    lines.append("  many_to_one_from_entities:")
                    for entity in many_to_one_entities:
                        lines.append(
                            f"  - sourceentity: {_yaml_scalar(entity['sourceentity'])}"
                        )

        return "\n".join(lines)

    @staticmethod
    def _attribute_dict(attribute: Attribute) -> dict:
        attribute_dict = {
            "attributename": attribute.attributename,
            "type": attribute.type,
        }
        if attribute.nullable:
            attribute_dict["nullable"] = True
        return attribute_dict

    @staticmethod
    def _append_attributes(lines: list[str], attributes: list[dict]) -> None:
        if not attributes:
            return
        lines.append("  attributes:")
        for attribute in attributes:
            lines.append(f"  - attributename: {_yaml_scalar(attribute['attributename'])}")
            lines.append(f"    type: {_yaml_scalar(attribute['type'])}")
            if attribute.get("nullable"):
                lines.append("    nullable: true")

    @staticmethod
    def _append_identification(lines: list[str], identification: dict) -> None:
        if not identification:
            lines.append("  identification: {}")
            return
        lines.append("  identification:")
        if "localkey" in identification:
            lines.append(f"    localkey: {_yaml_scalar(identification['localkey'])}")
        if "keytype" in identification:
            lines.append(f"    keytype: {_yaml_scalar(identification['keytype'])}")
        global_keys = identification.get("global", [])
        if global_keys:
            lines.append("    global:")
            for global_key in global_keys:
                lines.append(
                    f"    - targetentity: {_yaml_scalar(global_key['targetentity'])}"
                )
                if "role" in global_key:
                    lines.append(f"      role: {_yaml_scalar(global_key['role'])}")


class MermaidClassDiagramTranslationBuilder(ERSchemaTranslationBuilder):
    def __init__(self, direction: str = "LR") -> None:
        self.direction = direction
        self.class_order: list[str] = []
        self.class_attribute_members: dict[str, list[str]] = {}
        self.class_key_members: dict[str, list[str]] = {}
        self.entity_classes: set[str] = set()
        self.subentity_names: set[str] = set()
        self.valuelist_names: set[str] = set()
        self.valuelist_values: list[tuple[str, list[str]]] = []
        self.valuelists_by_sourceentity: dict[str, list[str]] = {}
        self.inheritance_edges: list[str] = []
        self.association_edges: list[str] = []
        self.relationship_edges: list[str] = []
        self.current_class_name: str | None = None
        self.current_class_has_key: bool = False
        self.current_relationship_entities: list[RelationshipEntity] = []

    def start_schema(self, er_schema: ERSchema) -> None:
        self.class_order = []
        self.class_attribute_members = {}
        self.class_key_members = {}
        self.entity_classes = {entity.entityname for entity in er_schema.entities}
        self.subentity_names = {
            subentity
            for inheritance in er_schema.inheritances
            for subentity in inheritance.subentities
        }
        self.valuelist_names = {
            valuelist.valuelistname for valuelist in er_schema.valuelists
        }
        self.valuelist_values = [
            (valuelist.valuelistname, list(valuelist.values))
            for valuelist in er_schema.valuelists
        ]
        self.valuelists_by_sourceentity = {}
        for valuelist in er_schema.valuelists:
            for entity in valuelist.many_to_one_from_entities:
                self._add_valuelist_usage(entity.entityname, valuelist.valuelistname)
        self.inheritance_edges = []
        self.association_edges = []
        self.relationship_edges = []
        self.current_class_name = None
        self.current_class_has_key = False
        self.current_relationship_entities = []

    def end_schema(self, er_schema: ERSchema) -> None:
        return None

    def start_entity(self, entity: Entity) -> None:
        self._start_class(entity.entityname)

    def add_entity_key(self, entity: Entity) -> None:
        self._add_key_member(
            f"**key**({entity.key} {_member_type(entity.keytype)})"
        )
        self.current_class_has_key = True

    def add_entity_attribute(self, entity: Entity, attribute: Attribute) -> None:
        visibility = "-" if attribute.nullable else "+"
        self._add_attribute_member(
            f"{visibility}{attribute.attributename} {_member_type(attribute.type)}"
        )

    def end_entity(self, entity: Entity) -> None:
        self._finalize_class(entity.entityname)

    def start_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        self._start_class(associative_entity.associationname)

    def start_identification(self, identification: Identification) -> None:
        if identification.localkey is not None:
            self._add_key_member(
                f"**local_key**({identification.localkey} "
                f"{_member_type(identification.keytype)})"
            )
            self.current_class_has_key = True

    def add_global_key(
        self, identification: Identification, global_key: GlobalKey
    ) -> None:
        global_key_name = global_key.role or global_key.targetentity
        self._add_key_member(f"**global_key**({global_key_name})")
        self.current_class_has_key = True
        self._add_association_edge(
            source=self._require_current_class_name(),
            target=global_key.targetentity,
            target_cardinality="ONE",
            label=global_key_name,
        )

    def end_identification(self, identification: Identification) -> None:
        return None

    def add_association(
        self, associative_entity: AssociativeEntity, association: Association
    ) -> None:
        if association.targetentity in self.valuelist_names:
            self._add_valuelist_usage(
                associative_entity.associationname, association.targetentity
            )
            return
        self._add_association_edge(
            source=associative_entity.associationname,
            target=association.targetentity,
            target_cardinality=association.cardinality,
            label=association.role or association.targetentity,
        )

    def add_associative_entity_attribute(
        self, associative_entity: AssociativeEntity, attribute: Attribute
    ) -> None:
        visibility = "-" if attribute.nullable else "+"
        self._add_attribute_member(
            f"{visibility}{attribute.attributename} {_member_type(attribute.type)}"
        )

    def end_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        self._finalize_class(associative_entity.associationname)

    def start_relationship(self, relationship: Relationship) -> None:
        self.current_relationship_entities = []

    def add_relationship_entity(
        self, relationship: Relationship, entity: RelationshipEntity
    ) -> None:
        self.current_relationship_entities.append(entity)

    def add_relationship_attribute(
        self, relationship: Relationship, attribute: Attribute
    ) -> None:
        return None

    def end_relationship(self, relationship: Relationship) -> None:
        if len(self.current_relationship_entities) == 2:
            left_entity, right_entity = self.current_relationship_entities
            self.relationship_edges.append(
                f'    {left_entity.entityname} "{_mermaid_cardinality(left_entity.cardinality)}" '
                f'-- "{_mermaid_cardinality(right_entity.cardinality)}" '
                f"{right_entity.entityname} : {relationship.relationshipname}"
            )
        self.current_relationship_entities = []

    def add_inheritance(self, inheritance: Inheritance) -> None:
        for subentity in inheritance.subentities:
            self.inheritance_edges.append(
                f"    {inheritance.superentity} <|-- {subentity}"
            )

    def start_valuelist(self, valuelist: ValueList) -> None:
        return None

    def add_many_to_one_entity(
        self, valuelist: ValueList, entity: ManyToOneEntity
    ) -> None:
        self._add_valuelist_usage(entity.entityname, valuelist.valuelistname)

    def end_valuelist(self, valuelist: ValueList) -> None:
        return None

    def build(self) -> str:
        lines = [
            "---",
            "config:",
            "  class:",
            "    hideEmptyMembersBox: true",
            "---",
            "classDiagram",
            f"    direction {self.direction}",
        ]

        if self.valuelist_values:
            lines.append('    note "Entries in Valuelists:')
            for valuelistname, values in self.valuelist_values:
                values_str = ", ".join(_mermaid_text(value) for value in values)
                lines.append(f"    {valuelistname}: {values_str}")
            lines.append('    "')

        for class_name in self.class_order:
            style_suffix = ":::entityStyle" if class_name in self.entity_classes else ""
            lines.append(f"    class {class_name}{style_suffix} {{")
            lines.extend(
                f"        {member}"
                for member in (
                    self.class_attribute_members[class_name]
                    + self.class_key_members[class_name]
                )
            )
            lines.append("    }")

        lines.extend(self.inheritance_edges)
        lines.extend(self.association_edges)
        lines.extend(self.relationship_edges)

        if self.entity_classes:
            lines.append("")
            lines.append(
                "    classDef entityStyle fill:#d0d0d0,stroke:#333,stroke-width:2px"
            )

        return "\n".join(lines)

    def _start_class(self, class_name: str) -> None:
        self.current_class_name = class_name
        self.current_class_has_key = False
        self.class_order.append(class_name)
        self.class_attribute_members[class_name] = []
        self.class_key_members[class_name] = []

    def _finalize_class(self, class_name: str, inherited_key: bool = True) -> None:
        if inherited_key and not self.current_class_has_key and class_name in self.subentity_names:
            self.class_key_members[class_name].append("**key**(inherited)")
        for valuelistname in self.valuelists_by_sourceentity.get(class_name, []):
            self.class_key_members[class_name].append(f"**vl**({valuelistname})")
        self.current_class_name = None
        self.current_class_has_key = False

    def _add_attribute_member(self, member: str) -> None:
        class_name = self._require_current_class_name()
        self.class_attribute_members[class_name].append(member)

    def _add_key_member(self, member: str) -> None:
        class_name = self._require_current_class_name()
        self.class_key_members[class_name].append(member)

    def _require_current_class_name(self) -> str:
        assert self.current_class_name is not None
        return self.current_class_name

    def _add_valuelist_usage(self, sourceentity: str, valuelistname: str) -> None:
        entity_valuelists = self.valuelists_by_sourceentity.setdefault(sourceentity, [])
        if valuelistname not in entity_valuelists:
            entity_valuelists.append(valuelistname)

    def _add_association_edge(
        self,
        source: str,
        target: str,
        target_cardinality: str | None,
        label: str,
    ) -> None:
        if target in self.valuelist_names:
            self._add_valuelist_usage(source, target)
            return
        self.association_edges.append(
            f'    {source} "0..*" -- "{_mermaid_cardinality(target_cardinality)}" '
            f"{target} : {label}"
        )


class RelAstTranslationBuilder(ERSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.entity_tables: list[Table] = []
        self.associative_tables: list[Table] = []
        self.relationship_tables: list[Table] = []
        self.datalists: list[DataList] = []
        self.tables_by_name: dict[str, Table] = {}
        self.entities_by_name: dict[str, Entity] = {}
        self.associative_entities_by_name: dict[str, AssociativeEntity] = {}
        self.subentity_to_superentity: dict[str, str] = {}
        self.valuelist_names: set[str] = set()
        self.structure_primary_keys: dict[str, list[Column]] = {}
        self.current_table: Table | None = None
        self.pending_associative_foreign_keys: list[ForeignKey] = []
        self.pending_associative_columns: list[Column] = []
        self.current_relationship_entities: list[RelationshipEntity] = []
        self.current_relationship_attributes: list[Attribute] = []

    def start_schema(self, er_schema: ERSchema) -> None:
        self.entity_tables = []
        self.associative_tables = []
        self.relationship_tables = []
        self.datalists = []
        self.tables_by_name = {}
        self.entities_by_name = {
            entity.entityname: entity for entity in er_schema.entities
        }
        self.associative_entities_by_name = {
            associative_entity.associationname: associative_entity
            for associative_entity in er_schema.associative_entities
        }
        self.subentity_to_superentity = {
            subentity: inheritance.superentity
            for inheritance in er_schema.inheritances
            for subentity in inheritance.subentities
        }
        self.valuelist_names = {
            valuelist.valuelistname for valuelist in er_schema.valuelists
        }
        self.structure_primary_keys = {}
        for structure_name in (
            list(self.entities_by_name) + list(self.associative_entities_by_name)
        ):
            self._resolve_primary_key_columns(structure_name)
        self.current_table = None
        self.pending_associative_foreign_keys = []
        self.pending_associative_columns = []
        self.current_relationship_entities = []
        self.current_relationship_attributes = []

    def end_schema(self, er_schema: ERSchema) -> None:
        return None

    def start_entity(self, entity: Entity) -> None:
        table = Table(tablename=entity.entityname)
        if entity.entityname in self.subentity_to_superentity:
            self._add_primary_key_columns(
                table,
                self._resolve_primary_key_columns(entity.entityname),
            )
        self.current_table = table

    def add_entity_key(self, entity: Entity) -> None:
        assert self.current_table is not None
        key_columns = self._resolve_primary_key_columns(entity.entityname)
        if entity.entityname not in self.subentity_to_superentity:
            self._add_primary_key_columns(self.current_table, key_columns)

    def add_entity_attribute(self, entity: Entity, attribute: Attribute) -> None:
        assert self.current_table is not None
        self.current_table.columns.append(
            Column(
                columnname=attribute.attributename,
                type=attribute.type,
                nullable=attribute.nullable,
            )
        )

    def end_entity(self, entity: Entity) -> None:
        assert self.current_table is not None
        self._register_table(self.current_table, self.entity_tables)
        self.current_table = None

    def start_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        table = Table(tablename=associative_entity.associationname)
        if associative_entity.associationname in self.subentity_to_superentity:
            self._add_primary_key_columns(
                table,
                self._resolve_primary_key_columns(associative_entity.associationname),
            )
        self.current_table = table
        self.pending_associative_foreign_keys = []
        self.pending_associative_columns = []

    def start_identification(self, identification: Identification) -> None:
        assert self.current_table is not None
        if identification.localkey is not None:
            self._add_primary_key_columns(
                self.current_table,
                [
                    Column(
                        columnname=identification.localkey,
                        type=_member_type(identification.keytype),
                    )
                ],
            )

    def add_global_key(
        self, identification: Identification, global_key: GlobalKey
    ) -> None:
        assert self.current_table is not None
        source_columns, target_columns = self._foreign_key_columns_for_target(
            global_key.targetentity,
            global_key.role,
        )
        self._add_primary_key_columns(self.current_table, source_columns)
        label = global_key.role or global_key.targetentity
        self._add_foreign_key(
            self.current_table,
            ForeignKey(
                fkname=f"fk_{self.current_table.tablename}_{label}",
                sourcecolumns=[column.columnname for column in source_columns],
                targettable=global_key.targetentity,
                targetcolumns=target_columns,
            ),
        )

    def end_identification(self, identification: Identification) -> None:
        return None

    def add_association(
        self, associative_entity: AssociativeEntity, association: Association
    ) -> None:
        assert self.current_table is not None
        if association.targetentity in self.valuelist_names:
            self._add_valuelist_foreign_key(
                associative_entity.associationname,
                association.targetentity,
            )
            return

        source_columns, target_columns = self._foreign_key_columns_for_target(
            association.targetentity,
            association.role,
        )
        for column in source_columns:
            self.pending_associative_columns.append(self._clone_column(column))
        label = association.role or association.targetentity
        self.pending_associative_foreign_keys.append(
            ForeignKey(
                fkname=f"fk_{associative_entity.associationname}_{label}_assoc",
                sourcecolumns=[column.columnname for column in source_columns],
                targettable=association.targetentity,
                targetcolumns=target_columns,
            )
        )

    def add_associative_entity_attribute(
        self, associative_entity: AssociativeEntity, attribute: Attribute
    ) -> None:
        assert self.current_table is not None
        self.current_table.columns.append(
            Column(
                columnname=attribute.attributename,
                type=attribute.type,
                nullable=attribute.nullable,
            )
        )

    def end_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        assert self.current_table is not None
        self._add_columns(self.current_table, self.pending_associative_columns)
        for foreign_key in self.pending_associative_foreign_keys:
            self._add_foreign_key(self.current_table, foreign_key)
        self._register_table(self.current_table, self.associative_tables)
        self.current_table = None
        self.pending_associative_foreign_keys = []
        self.pending_associative_columns = []

    def start_relationship(self, relationship: Relationship) -> None:
        self.current_relationship_entities = []
        self.current_relationship_attributes = []

    def add_relationship_entity(
        self, relationship: Relationship, entity: RelationshipEntity
    ) -> None:
        self.current_relationship_entities.append(entity)

    def add_relationship_attribute(
        self, relationship: Relationship, attribute: Attribute
    ) -> None:
        self.current_relationship_attributes.append(attribute)

    def end_relationship(self, relationship: Relationship) -> None:
        if len(self.current_relationship_entities) != 2:
            self.current_relationship_entities = []
            self.current_relationship_attributes = []
            return

        left_entity, right_entity = self.current_relationship_entities
        if (
            not self.current_relationship_attributes
            and self._is_many_cardinality(left_entity.cardinality)
            and not self._is_many_cardinality(right_entity.cardinality)
        ):
            self._add_relationship_foreign_key(source=left_entity, target=right_entity, relationshipname=relationship.relationshipname)
        elif (
            not self.current_relationship_attributes
            and self._is_many_cardinality(right_entity.cardinality)
            and not self._is_many_cardinality(left_entity.cardinality)
        ):
            self._add_relationship_foreign_key(source=right_entity, target=left_entity, relationshipname=relationship.relationshipname)
        else:
            bridge_table = Table(tablename=relationship.relationshipname)
            for entity in self.current_relationship_entities:
                source_columns, target_columns = self._foreign_key_columns_for_target(
                    entity.entityname,
                    entity.role,
                )
                self._add_primary_key_columns(bridge_table, source_columns)
                label = entity.role or entity.entityname
                self._add_foreign_key(
                    bridge_table,
                    ForeignKey(
                        fkname=f"fk_{relationship.relationshipname}_{label}",
                        sourcecolumns=[column.columnname for column in source_columns],
                        targettable=entity.entityname,
                        targetcolumns=target_columns,
                    ),
                )
            for attribute in self.current_relationship_attributes:
                bridge_table.columns.append(
                    Column(
                        columnname=attribute.attributename,
                        type=attribute.type,
                        nullable=attribute.nullable,
                    )
                )
            self._register_table(bridge_table, self.relationship_tables)

        self.current_relationship_entities = []
        self.current_relationship_attributes = []

    def add_inheritance(self, inheritance: Inheritance) -> None:
        super_primary_key = self._resolve_primary_key_columns(inheritance.superentity)
        for subentity in inheritance.subentities:
            subentity_table = self.tables_by_name[subentity]
            self._add_foreign_key(
                subentity_table,
                ForeignKey(
                    fkname=f"fk_{subentity}_{inheritance.superentity}",
                    sourcecolumns=[column.columnname for column in super_primary_key],
                    targettable=inheritance.superentity,
                    targetcolumns=[column.columnname for column in super_primary_key],
                ),
            )

    def start_valuelist(self, valuelist: ValueList) -> None:
        valuelist_table = Table(
            tablename=valuelist.valuelistname,
            columns=[
                Column(columnname="ID", type="INTEGER"),
                Column(columnname="Description", type="TEXT"),
                Column(columnname="IsValid", type="INTEGER"),
                Column(columnname="SortOrder", type="INTEGER"),
            ],
            primary_key=["ID"],
        )
        self._register_table(valuelist_table, self.entity_tables)
        self.datalists.append(
            DataList(tablename=valuelist.valuelistname, values=list(valuelist.values))
        )

    def add_many_to_one_entity(
        self, valuelist: ValueList, entity: ManyToOneEntity
    ) -> None:
        self._add_valuelist_foreign_key(entity.entityname, valuelist.valuelistname)

    def end_valuelist(self, valuelist: ValueList) -> None:
        return None

    def build(self) -> RelSchema:
        return RelSchema(
            tables=self.entity_tables + self.associative_tables + self.relationship_tables,
            datalists=self.datalists,
        )

    def _resolve_primary_key_columns(self, structure_name: str) -> list[Column]:
        existing = self.structure_primary_keys.get(structure_name)
        if existing is not None:
            return [self._clone_column(column) for column in existing]

        if structure_name in self.subentity_to_superentity:
            resolved = self._resolve_primary_key_columns(
                self.subentity_to_superentity[structure_name]
            )
            self.structure_primary_keys[structure_name] = [
                self._clone_column(column) for column in resolved
            ]
            return resolved

        if structure_name in self.entities_by_name:
            entity = self.entities_by_name[structure_name]
            resolved = (
                [
                    Column(
                        columnname=entity.key,
                        type=_member_type(entity.keytype),
                    )
                ]
                if entity.key is not None
                else []
            )
            self.structure_primary_keys[structure_name] = [
                self._clone_column(column) for column in resolved
            ]
            return resolved

        if structure_name in self.associative_entities_by_name:
            associative_entity = self.associative_entities_by_name[structure_name]
            resolved: list[Column] = []
            identification = associative_entity.identification
            if identification is not None:
                if identification.localkey is not None:
                    resolved.append(
                        Column(
                            columnname=identification.localkey,
                            type=_member_type(identification.keytype),
                        )
                    )
                for global_key in identification.global_keys:
                    foreign_key_columns, _ = self._foreign_key_columns_for_target(
                        global_key.targetentity,
                        global_key.role,
                    )
                    resolved.extend(foreign_key_columns)
            self.structure_primary_keys[structure_name] = [
                self._clone_column(column) for column in resolved
            ]
            return resolved

        if structure_name in self.valuelist_names:
            return [Column(columnname="ID", type="INTEGER")]

        raise KeyError(f"Unknown structure '{structure_name}'.")

    def _foreign_key_columns_for_target(
        self,
        target_name: str,
        role: str | None,
    ) -> tuple[list[Column], list[str]]:
        target_primary_key = self._resolve_primary_key_columns(target_name)
        if len(target_primary_key) == 1:
            primary_key_column = target_primary_key[0]
            source_column_name = self._relationship_column_name(
                role,
                primary_key_column.columnname,
            )
            return (
                [
                    Column(
                        columnname=source_column_name,
                        type=primary_key_column.type,
                    )
                ],
                [primary_key_column.columnname],
            )
        return (
            [self._clone_column(column) for column in target_primary_key],
            [column.columnname for column in target_primary_key],
        )

    def _relationship_column_name(
        self,
        role: str | None,
        target_primary_key_column: str,
    ) -> str:
        if role is None:
            return target_primary_key_column
        if target_primary_key_column.endswith("ID"):
            return f"{role}ID"
        return f"{role}{target_primary_key_column}"

    def _add_relationship_foreign_key(
        self,
        source: RelationshipEntity,
        target: RelationshipEntity,
        relationshipname: str,
    ) -> None:
        source_table = self.tables_by_name[source.entityname]
        source_columns, target_columns = self._foreign_key_columns_for_target(
            target.entityname,
            target.role,
        )
        self._add_columns(source_table, source_columns)
        self._add_foreign_key(
            source_table,
            ForeignKey(
                fkname=f"fk_{relationshipname}",
                sourcecolumns=[column.columnname for column in source_columns],
                targettable=target.entityname,
                targetcolumns=target_columns,
            ),
        )

    def _add_valuelist_foreign_key(self, source_name: str, valuelistname: str) -> None:
        source_table = self.tables_by_name[source_name]
        column_name = f"{valuelistname}ID"
        self._add_columns(source_table, [Column(columnname=column_name, type="INTEGER")])
        self._add_foreign_key(
            source_table,
            ForeignKey(
                fkname=f"fk_{source_name}_{valuelistname}",
                sourcecolumns=[column_name],
                targettable=valuelistname,
                targetcolumns=["ID"],
            ),
        )

    def _register_table(self, table: Table, table_list: list[Table]) -> None:
        self.tables_by_name[table.tablename] = table
        table_list.append(table)

    def _add_primary_key_columns(self, table: Table, columns: list[Column]) -> None:
        self._add_columns(table, columns)
        for column in columns:
            if column.columnname not in table.primary_key:
                table.primary_key.append(column.columnname)

    def _add_columns(self, table: Table, columns: list[Column]) -> None:
        known_columns = {column.columnname for column in table.columns}
        for column in columns:
            if column.columnname in known_columns:
                continue
            table.columns.append(self._clone_column(column))
            known_columns.add(column.columnname)

    def _add_foreign_key(self, table: Table, foreign_key: ForeignKey) -> None:
        for existing_foreign_key in table.foreign_keys:
            if (
                existing_foreign_key.sourcecolumns == foreign_key.sourcecolumns
                and existing_foreign_key.targettable == foreign_key.targettable
                and existing_foreign_key.targetcolumns == foreign_key.targetcolumns
            ):
                return
        table.foreign_keys.append(foreign_key)

    @staticmethod
    def _clone_column(column: Column) -> Column:
        return Column(
            columnname=column.columnname,
            type=column.type,
            nullable=column.nullable,
        )

    @staticmethod
    def _is_many_cardinality(cardinality: str | None) -> bool:
        return cardinality in {"MANY", "OPTIONAL_MANY"}


def translate_er_ast_to_rel_ast(er_schema: ERSchema) -> RelSchema:
    builder = RelAstTranslationBuilder()
    visitor = ERSchemaTranslationVisitor(builder)
    visitor.visit(er_schema)
    return builder.build()
