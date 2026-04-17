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
from edurel.syntax.er_yaml_schema import schema
from edurel.translation.er_trans import (
    ERSchemaTranslationBuilder,
    ERSchemaTranslationVisitor,
    YamlTranslationBuilder,
)
from edurel.utils.yaml import parse_yaml


class RecordingBuilder(ERSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.events: list[str] = []

    def start_schema(self, er_schema: ERSchema) -> None:
        self.events.append("start_schema")

    def end_schema(self, er_schema: ERSchema) -> None:
        self.events.append("end_schema")

    def start_entity(self, entity: Entity) -> None:
        self.events.append(f"start_entity:{entity.entityname}")

    def add_entity_key(self, entity: Entity) -> None:
        self.events.append(f"entity_key:{entity.entityname}.{entity.key}")

    def add_entity_attribute(self, entity: Entity, attribute: Attribute) -> None:
        self.events.append(f"entity_attribute:{entity.entityname}.{attribute.attributename}")

    def end_entity(self, entity: Entity) -> None:
        self.events.append(f"end_entity:{entity.entityname}")

    def start_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        self.events.append(
            f"start_associative_entity:{associative_entity.associationname}"
        )

    def start_identification(self, identification: Identification) -> None:
        self.events.append("start_identification")

    def add_global_key(
        self, identification: Identification, global_key: GlobalKey
    ) -> None:
        self.events.append(f"global_key:{global_key.targetentity}")

    def end_identification(self, identification: Identification) -> None:
        self.events.append("end_identification")

    def add_association(
        self, associative_entity: AssociativeEntity, association: Association
    ) -> None:
        self.events.append(
            f"association:{associative_entity.associationname}->{association.targetentity}"
        )

    def add_associative_entity_attribute(
        self, associative_entity: AssociativeEntity, attribute: Attribute
    ) -> None:
        self.events.append(
            "associative_attribute:"
            f"{associative_entity.associationname}.{attribute.attributename}"
        )

    def end_associative_entity(self, associative_entity: AssociativeEntity) -> None:
        self.events.append(f"end_associative_entity:{associative_entity.associationname}")

    def start_relationship(self, relationship: Relationship) -> None:
        self.events.append(f"start_relationship:{relationship.relationshipname}")

    def add_relationship_entity(
        self, relationship: Relationship, entity: RelationshipEntity
    ) -> None:
        self.events.append(
            f"relationship_entity:{relationship.relationshipname}->{entity.entityname}"
        )

    def add_relationship_attribute(
        self, relationship: Relationship, attribute: Attribute
    ) -> None:
        self.events.append(
            f"relationship_attribute:{relationship.relationshipname}.{attribute.attributename}"
        )

    def end_relationship(self, relationship: Relationship) -> None:
        self.events.append(f"end_relationship:{relationship.relationshipname}")

    def add_inheritance(self, inheritance: Inheritance) -> None:
        self.events.append(f"inheritance:{inheritance.superentity}")

    def start_valuelist(self, valuelist: ValueList) -> None:
        self.events.append(f"start_valuelist:{valuelist.valuelistname}")

    def add_many_to_one_entity(
        self, valuelist: ValueList, entity: ManyToOneEntity
    ) -> None:
        self.events.append(f"many_to_one:{valuelist.valuelistname}->{entity.entityname}")

    def end_valuelist(self, valuelist: ValueList) -> None:
        self.events.append(f"end_valuelist:{valuelist.valuelistname}")

    def build(self) -> str:
        return "\n".join(self.events)


def test_translation_visitor_traverses_er_schema_in_canonical_order() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(
                entityname="User",
                key="user_id",
                keytype="INTEGER",
                attributes=[Attribute(attributename="email", type="VARCHAR(255)")],
            )
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    localkey="enrollment_id",
                    keytype="INTEGER",
                    global_keys=[GlobalKey(targetentity="User", role="student")],
                ),
                associations=[
                    Association(
                        targetentity="Course",
                        role="course",
                        cardinality="MANY",
                    )
                ],
                attributes=[Attribute(attributename="created_at", type="TIMESTAMP")],
            )
        ],
        relationships=[
            Relationship(
                relationshipname="Teaches",
                entities=[
                    RelationshipEntity(
                        entityname="Teacher",
                        role="teacher",
                        cardinality="ONE",
                    ),
                    RelationshipEntity(
                        entityname="Course",
                        role="course",
                        cardinality="MANY",
                    ),
                ],
                attributes=[Attribute(attributename="starts_on", type="DATE")],
            )
        ],
        inheritances=[
            Inheritance(
                superentity="Person",
                subentities=["Student", "Teacher"],
                implementation="ONE_TABLE",
            )
        ],
        valuelists=[
            ValueList(
                valuelistname="Status",
                values=["active", "inactive"],
                many_to_one_from_entities=[ManyToOneEntity(entityname="User")],
            )
        ],
    )

    builder = RecordingBuilder()
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.events == [
        "start_schema",
        "start_entity:User",
        "entity_key:User.user_id",
        "entity_attribute:User.email",
        "end_entity:User",
        "start_associative_entity:Enrollment",
        "start_identification",
        "global_key:User",
        "end_identification",
        "association:Enrollment->Course",
        "associative_attribute:Enrollment.created_at",
        "end_associative_entity:Enrollment",
        "start_relationship:Teaches",
        "relationship_entity:Teaches->Teacher",
        "relationship_entity:Teaches->Course",
        "relationship_attribute:Teaches.starts_on",
        "end_relationship:Teaches",
        "inheritance:Person",
        "start_valuelist:Status",
        "many_to_one:Status->User",
        "end_valuelist:Status",
        "end_schema",
    ]


def test_yaml_translation_builder_serializes_er_ast_to_valid_yaml() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(
                entityname="User",
                key="user_id",
                keytype="INTEGER",
                attributes=[
                    Attribute(attributename="email", type="VARCHAR(255)"),
                    Attribute(
                        attributename="nickname",
                        type="VARCHAR(50)",
                        nullable=True,
                    ),
                ],
            )
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    localkey="enrollment_id",
                    keytype="INTEGER",
                    global_keys=[
                        GlobalKey(targetentity="User", role="student"),
                        GlobalKey(targetentity="Course"),
                    ],
                ),
                associations=[
                    Association(
                        targetentity="Status",
                        role="status",
                        cardinality="OPTIONAL_ONE",
                    )
                ],
                attributes=[Attribute(attributename="created_at", type="TIMESTAMP")],
            )
        ],
        relationships=[
            Relationship(
                relationshipname="Teaches",
                entities=[
                    RelationshipEntity(
                        entityname="Teacher",
                        role="teacher",
                        cardinality="ONE",
                    ),
                    RelationshipEntity(
                        entityname="Course",
                        role="course",
                        cardinality="MANY",
                    ),
                ],
                attributes=[Attribute(attributename="starts_on", type="DATE")],
            )
        ],
        inheritances=[
            Inheritance(
                superentity="Person",
                subentities=["Student", "Teacher"],
                implementation="ONE_TABLE_PER_ENTITY",
            )
        ],
        valuelists=[
            ValueList(
                valuelistname="Status",
                values=["active", "inactive"],
                many_to_one_from_entities=[
                    ManyToOneEntity(entityname="User"),
                    ManyToOneEntity(entityname="Enrollment"),
                ],
            )
        ],
    )

    builder = YamlTranslationBuilder()
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)
    yaml_text = builder.build()

    assert parse_yaml(yaml_text, schema) == {
        "entities": [
            {
                "entityname": "User",
                "key": "user_id",
                "keytype": "INTEGER",
                "attributes": [
                    {"attributename": "email", "type": "VARCHAR(255)"},
                    {
                        "attributename": "nickname",
                        "type": "VARCHAR(50)",
                        "nullable": True,
                    },
                ],
            }
        ],
        "associative_entities": [
            {
                "associationname": "Enrollment",
                "identification": {
                    "localkey": "enrollment_id",
                    "keytype": "INTEGER",
                    "global": [
                        {"targetentity": "User", "role": "student"},
                        {"targetentity": "Course"},
                    ],
                },
                "associations": [
                    {
                        "targetentity": "Status",
                        "role": "status",
                        "cardinality": "OPTIONAL_ONE",
                    }
                ],
                "attributes": [
                    {"attributename": "created_at", "type": "TIMESTAMP"}
                ],
            }
        ],
        "relationships": [
            {
                "relationshipname": "Teaches",
                "entities": [
                    {
                        "targetentity": "Teacher",
                        "role": "teacher",
                        "cardinality": "ONE",
                    },
                    {
                        "targetentity": "Course",
                        "role": "course",
                        "cardinality": "MANY",
                    },
                ],
                "attributes": [{"attributename": "starts_on", "type": "DATE"}],
            }
        ],
        "inheritances": [
            {
                "superentity": "Person",
                "subentities": ["Student", "Teacher"],
                "implementation": "ONE_TABLE_PER_ENTITY",
            }
        ],
        "valuelists": [
            {
                "valuelistname": "Status",
                "values": ["active", "inactive"],
                "many_to_one_from_entities": [
                    {"sourceentity": "User"},
                    {"sourceentity": "Enrollment"},
                ],
            }
        ],
    }
