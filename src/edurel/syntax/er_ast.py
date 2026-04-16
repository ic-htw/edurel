from dataclasses import dataclass, field


@dataclass
class Attribute:
    """Represents an ER attribute with type and nullable flag."""

    attributename: str
    type: str
    nullable: bool = False

    def __str__(self) -> str:
        nullable_str = " (null)" if self.nullable else " (not null)"
        return f"{self.attributename}: {self.type}{nullable_str}"


@dataclass
class Entity:
    """Represents an entity with an optional local key and attributes."""

    entityname: str
    key: str | None = None
    keytype: str | None = None
    attributes: list[Attribute] = field(default_factory=list)

    def __str__(self) -> str:
        result = f"Entity: {self.entityname}"
        if self.key:
            keytype_str = f" ({self.keytype})" if self.keytype else ""
            result += f"\n  Key: {self.key}{keytype_str}"
        if self.attributes:
            attributes_str = "\n    ".join(str(attribute) for attribute in self.attributes)
            result += f"\n  Attributes:\n    {attributes_str}"
        return result


@dataclass
class GlobalKey:
    """Represents a global identification reference."""

    targetentity: str
    role: str | None = None

    def __str__(self) -> str:
        role_str = f": role: {self.role}" if self.role else ""
        return f"{self.targetentity}{role_str}"


@dataclass
class Identification:
    """Represents associative entity identification metadata."""

    localkey: str | None = None
    keytype: str | None = None
    global_keys: list[GlobalKey] = field(default_factory=list)

    def __str__(self) -> str:
        if self.localkey:
            keytype_str = f" ({self.keytype})" if self.keytype else ""
            result = f"Local Key: {self.localkey}{keytype_str}"
        else:
            result = "Identification"
        if self.global_keys:
            globals_str = "\n    ".join(str(global_key) for global_key in self.global_keys)
            result += f"\n  Global Keys:\n    {globals_str}"
        return result


@dataclass
class Association:
    """Represents an association target and optional role/cardinality."""

    targetentity: str
    role: str | None = None
    cardinality: str | None = None

    def __str__(self) -> str:
        parts = [self.targetentity]
        if self.role:
            parts.append(f"role={self.role}")
        if self.cardinality:
            parts.append(f"cardinality={self.cardinality}")
        return ", ".join(parts)


@dataclass
class AssociativeEntity:
    """Represents an associative entity with identification and associations."""

    associationname: str
    identification: Identification | None = None
    associations: list[Association] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)

    def __str__(self) -> str:
        result = f"Associative Entity: {self.associationname}"
        if self.identification:
            result += f"\n  Identification: {self.identification}"
        if self.associations:
            associations_str = "\n    ".join(
                str(association) for association in self.associations
            )
            result += f"\n  Associations:\n    {associations_str}"
        if self.attributes:
            attributes_str = "\n    ".join(str(attribute) for attribute in self.attributes)
            result += f"\n  Attributes:\n    {attributes_str}"
        return result


@dataclass
class RelationshipEntity:
    """Represents an entity participating in a relationship."""

    entityname: str
    role: str | None = None
    cardinality: str | None = None

    def __str__(self) -> str:
        parts = [self.entityname]
        if self.role:
            parts.append(f"role={self.role}")
        if self.cardinality:
            parts.append(f"cardinality={self.cardinality}")
        return ", ".join(parts)


@dataclass
class Relationship:
    """Represents a relationship and its participants."""

    relationshipname: str
    entities: list[RelationshipEntity] = field(default_factory=list)
    attributes: list[Attribute] = field(default_factory=list)

    def __str__(self) -> str:
        entities_str = "\n    ".join(str(entity) for entity in self.entities)
        result = f"Relationship: {self.relationshipname}\n  Entities:\n    {entities_str}"
        if self.attributes:
            attributes_str = "\n    ".join(str(attribute) for attribute in self.attributes)
            result += f"\n  Attributes:\n    {attributes_str}"
        return result


@dataclass
class Inheritance:
    """Represents an inheritance hierarchy."""

    superentity: str
    subentities: list[str] = field(default_factory=list)
    implementation: str | None = None

    def __str__(self) -> str:
        subentities_str = ", ".join(self.subentities)
        result = f"Inheritance: {self.superentity} -> [{subentities_str}]"
        if self.implementation:
            result += f"\n  Implementation: {self.implementation}"
        return result


@dataclass
class ManyToOneEntity:
    """Represents an entity using a value list in a many-to-one relation."""

    entityname: str

    def __str__(self) -> str:
        return self.entityname


@dataclass
class ValueList:
    """Represents a value list and the entities that use it."""

    valuelistname: str
    values: list[str] = field(default_factory=list)
    many_to_one_from_entities: list[ManyToOneEntity] = field(default_factory=list)

    def __str__(self) -> str:
        values_str = ", ".join(self.values)
        result = f"ValueList: {self.valuelistname}\n  Values: {values_str}"
        if self.many_to_one_from_entities:
            entities_str = ", ".join(
                entity.entityname for entity in self.many_to_one_from_entities
            )
            result += f"\n  Many-to-one From: {entities_str}"
        return result


@dataclass
class ERSchema:
    """Complete ER schema AST."""

    entities: list[Entity] = field(default_factory=list)
    associative_entities: list[AssociativeEntity] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    inheritances: list[Inheritance] = field(default_factory=list)
    valuelists: list[ValueList] = field(default_factory=list)

    def __str__(self) -> str:
        sections = []
        if self.entities:
            entities_str = "\n\n".join(str(entity) for entity in self.entities)
            sections.append(f"=== ENTITIES ===\n{entities_str}")
        if self.associative_entities:
            associative_entities_str = "\n\n".join(
                str(associative_entity)
                for associative_entity in self.associative_entities
            )
            sections.append(f"=== ASSOCIATIVE ENTITIES ===\n{associative_entities_str}")
        if self.relationships:
            relationships_str = "\n\n".join(
                str(relationship) for relationship in self.relationships
            )
            sections.append(f"=== RELATIONSHIPS ===\n{relationships_str}")
        if self.inheritances:
            inheritances_str = "\n\n".join(
                str(inheritance) for inheritance in self.inheritances
            )
            sections.append(f"=== INHERITANCES ===\n{inheritances_str}")
        if self.valuelists:
            valuelists_str = "\n\n".join(str(valuelist) for valuelist in self.valuelists)
            sections.append(f"=== VALUELISTS ===\n{valuelists_str}")
        return "\n\n".join(sections) if sections else "No ER schema elements"


class ERAstFactory:
    """Builds the ER schema AST from parsed YAML data."""

    @classmethod
    def create_schema(cls, data: dict) -> ERSchema:
        return ERSchema(
            entities=[cls.create_entity(entity) for entity in data.get("entities", [])],
            associative_entities=[
                cls.create_associative_entity(associative_entity)
                for associative_entity in data.get("associative_entities", [])
            ],
            relationships=[
                cls.create_relationship(relationship)
                for relationship in data.get("relationships", [])
            ],
            inheritances=[
                cls.create_inheritance(inheritance)
                for inheritance in data.get("inheritances", [])
            ],
            valuelists=[
                cls.create_valuelist(valuelist)
                for valuelist in data.get("valuelists", [])
            ],
        )

    @staticmethod
    def create_attribute(data: dict) -> Attribute:
        return Attribute(
            attributename=data["attributename"],
            type=data["type"],
            nullable=data.get("nullable", False),
        )

    @classmethod
    def create_entity(cls, data: dict) -> Entity:
        return Entity(
            entityname=data["entityname"],
            key=data.get("key"),
            keytype=data.get("keytype"),
            attributes=[
                cls.create_attribute(attribute)
                for attribute in data.get("attributes", [])
            ],
        )

    @staticmethod
    def create_global_key(data: dict) -> GlobalKey:
        return GlobalKey(
            targetentity=data["targetentity"],
            role=data.get("role"),
        )

    @classmethod
    def create_identification(cls, data: dict) -> Identification:
        return Identification(
            localkey=data.get("localkey"),
            keytype=data.get("keytype"),
            global_keys=[
                cls.create_global_key(global_key)
                for global_key in data.get("global", [])
            ],
        )

    @staticmethod
    def create_association(data: dict) -> Association:
        return Association(
            targetentity=data["targetentity"],
            role=data.get("role"),
            cardinality=data.get("cardinality"),
        )

    @classmethod
    def create_associative_entity(cls, data: dict) -> AssociativeEntity:
        identification_data = data.get("identification")
        return AssociativeEntity(
            associationname=data["associationname"],
            identification=(
                cls.create_identification(identification_data)
                if identification_data
                else None
            ),
            associations=[
                cls.create_association(association)
                for association in data.get("associations", [])
            ],
            attributes=[
                cls.create_attribute(attribute)
                for attribute in data.get("attributes", [])
            ],
        )

    @staticmethod
    def create_relationship_entity(data: dict) -> RelationshipEntity:
        return RelationshipEntity(
            entityname=data["entityname"],
            role=data.get("role"),
            cardinality=data.get("cardinality"),
        )

    @classmethod
    def create_relationship(cls, data: dict) -> Relationship:
        return Relationship(
            relationshipname=data["relationshipname"],
            entities=[
                cls.create_relationship_entity(entity)
                for entity in data.get("entities", [])
            ],
            attributes=[
                cls.create_attribute(attribute)
                for attribute in data.get("attributes", [])
            ],
        )

    @staticmethod
    def create_inheritance(data: dict) -> Inheritance:
        return Inheritance(
            superentity=data["superentity"],
            subentities=list(data.get("subentities", [])),
            implementation=data.get("implementation"),
        )

    @staticmethod
    def create_many_to_one_entity(data: dict) -> ManyToOneEntity:
        return ManyToOneEntity(entityname=data["entityname"])

    @classmethod
    def create_valuelist(cls, data: dict) -> ValueList:
        return ValueList(
            valuelistname=data["valuelistname"],
            values=list(data.get("values", [])),
            many_to_one_from_entities=[
                cls.create_many_to_one_entity(entity)
                for entity in data.get("many_to_one_from_entities", [])
            ],
        )
