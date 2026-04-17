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
