from textwrap import dedent

from edurel.syntax.er_ast import (
    Association,
    AssociativeEntity,
    Attribute,
    ERAstFactory,
    Entity,
    ERSchema,
    GlobalKey,
    Identification,
    Inheritance,
    validate_ast,
    ManyToOneEntity,
    Relationship,
    RelationshipEntity,
    ValueList,
)
from edurel.syntax.er_yaml_schema import schema
from edurel.translation.er_trans import (
    ERSchemaTranslationBuilder,
    ERSchemaTranslationVisitor,
    MermaidClassDiagramTranslationBuilder,
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


def test_mermaid_class_diagram_translation_builder_serializes_ast_from_yaml() -> None:
    yaml_text = dedent(
        """
        entities:
        - entityname: Person
          key: PID
          attributes:
          - attributename: Name
            type: TEXT

        - entityname: Semester
          key: SID
          attributes:
          - attributename: Bez
            type: TEXT
          - attributename: Beginn
            type: DATE
          - attributename: Ende
            type: DATE
          - attributename: VLBeginn
            type: DATE
          - attributename: VLEnde
            type: DATE

        - entityname: Modul
          key: MID
          attributes:
          - attributename: Bez
            type: TEXT
          - attributename: CP
            type: INTEGER
          - attributename: Regelsemester
            type: INTEGER

        - entityname: Raum
          key: RID
          attributes:
          - attributename: RaumNr
            type: TEXT

        - entityname: Termin
          key: TID

        - entityname: Einzeltermin
          attributes:
          - attributename: DatumUhrzeitVon
            type: DATE
          - attributename: DatumUhrzeitBis
            type: DATE

        - entityname: Zeitblock
          key: ZBID
          attributes:
          - attributename: UhrzeitVon
            type: TIME
          - attributename: UhrzeitBis
            type: TIME

        associative_entities:
        - associationname: Wochentermin
          associations:
          - targetentity: Zeitblock
            cardinality: ONE

        - associationname: PersonRolle
          identification:
            localkey: PersonRolleID
          associations:
          - targetentity: Person
            cardinality: ONE
          - targetentity: Rolle
            cardinality: ONE
          attributes:
          - attributename: DatumBeginn
            type: DATE
          - attributename: DatumEnde
            type: DATE
            nullable: TRUE

        - associationname: Lehrperson
          attributes:
          - attributename: Steuernummer
            type: TEXT

        - associationname: StudentIn
          attributes:
          - attributename: MatrNo
            type: TEXT

        - associationname: Sonstige

        - associationname: ModulBT
          identification:
            localkey: ModulBTID
          associations:
          - targetentity: Modul
            cardinality: ONE
          attributes:
          - attributename: SWS
            type: INTEGER

        - associationname: Kurs
          identification:
            localkey: KursID
          associations:
          - targetentity: Semester
            cardinality: ONE
          - targetentity: Modul
            cardinality: ONE
          attributes:
          - attributename: KursInfo
            type: TEXT

        - associationname: KursBT
          identification:
            localkey: KursBTID
          associations:
          - targetentity: Kurs
            cardinality: ONE
          - targetentity: ModulBT
            cardinality: ONE
          - targetentity: Raum
            cardinality: ONE
          - targetentity: Lehrperson
            cardinality: ONE
          - targetentity: Termin
            cardinality: ONE
          attributes:
          - attributename: KursBTInfo
            type: TEXT

        - associationname: Belegung
          identification:
            global:
            - targetentity: KursBT
            - targetentity: StudentIn
          attributes:
          - attributename: ErstelltAm
            type: DATE

        inheritances:
        - superentity: PersonRolle
          subentities:
          - Lehrperson
          - StudentIn
          - Sonstige

        - superentity: Termin
          subentities:
          - Einzeltermin
          - Wochentermin

        valuelists:
        - valuelistname: Rolle
          values:
          - Lehrperson
          - StudentIn
          - Verwaltung
          - Sicherheit
          many_to_one_from_entities:
          - sourceentity: PersonRolle

        - valuelistname: Modulart
          values:
          - Pflicht
          - Wahlpflicht
          - Wahl
          many_to_one_from_entities:
          - sourceentity: Modul

        - valuelistname: ModulBTArt
          values:
          - SL
          - PCÜ
          - Ü
          many_to_one_from_entities:
          - sourceentity: ModulBT

        - valuelistname: Belegungsstatus
          values:
          - Angemeldet
          - Abgemeldet
          - Zugelassen
          - Abgelehnt
          many_to_one_from_entities:
          - sourceentity: Belegung

        - valuelistname: Tag
          values:
          - Mo
          - Di
          - Mi
          - Do
          - Fr
          - Sa
          - So
          many_to_one_from_entities:
          - sourceentity: Wochentermin
        """
    ).strip()

    er_schema = ERAstFactory.create_schema(parse_yaml(yaml_text, schema))
    validate_ast(er_schema)

    builder = MermaidClassDiagramTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
        ---
        classDiagram
            direction LR
            note "Entries in Valuelists:
            Rolle: Lehrperson, StudentIn, Verwaltung, Sicherheit
            Modulart: Pflicht, Wahlpflicht, Wahl
            ModulBTArt: SL, PCÜ, Ü
            Belegungsstatus: Angemeldet, Abgemeldet, Zugelassen, Abgelehnt
            Tag: Mo, Di, Mi, Do, Fr, Sa, So
            "
            class Person:::entityStyle {
                +Name TEXT
                **key**(PID INTEGER)
            }
            class Semester:::entityStyle {
                +Bez TEXT
                +Beginn DATE
                +Ende DATE
                +VLBeginn DATE
                +VLEnde DATE
                **key**(SID INTEGER)
            }
            class Modul:::entityStyle {
                +Bez TEXT
                +CP INTEGER
                +Regelsemester INTEGER
                **key**(MID INTEGER)
                **vl**(Modulart)
            }
            class Raum:::entityStyle {
                +RaumNr TEXT
                **key**(RID INTEGER)
            }
            class Termin:::entityStyle {
                **key**(TID INTEGER)
            }
            class Einzeltermin:::entityStyle {
                +DatumUhrzeitVon DATE
                +DatumUhrzeitBis DATE
                **key**(inherited)
            }
            class Zeitblock:::entityStyle {
                +UhrzeitVon TIME
                +UhrzeitBis TIME
                **key**(ZBID INTEGER)
            }
            class Wochentermin {
                **key**(inherited)
                **vl**(Tag)
            }
            class PersonRolle {
                +DatumBeginn DATE
                -DatumEnde DATE
                **local_key**(PersonRolleID INTEGER)
                **vl**(Rolle)
            }
            class Lehrperson {
                +Steuernummer TEXT
                **key**(inherited)
            }
            class StudentIn {
                +MatrNo TEXT
                **key**(inherited)
            }
            class Sonstige {
                **key**(inherited)
            }
            class ModulBT {
                +SWS INTEGER
                **local_key**(ModulBTID INTEGER)
                **vl**(ModulBTArt)
            }
            class Kurs {
                +KursInfo TEXT
                **local_key**(KursID INTEGER)
            }
            class KursBT {
                +KursBTInfo TEXT
                **local_key**(KursBTID INTEGER)
            }
            class Belegung {
                +ErstelltAm DATE
                **global_key**(KursBT)
                **global_key**(StudentIn)
                **vl**(Belegungsstatus)
            }
            PersonRolle <|-- Lehrperson
            PersonRolle <|-- StudentIn
            PersonRolle <|-- Sonstige
            Termin <|-- Einzeltermin
            Termin <|-- Wochentermin
            Wochentermin "0..*" -- "1" Zeitblock : Zeitblock
            PersonRolle "0..*" -- "1" Person : Person
            ModulBT "0..*" -- "1" Modul : Modul
            Kurs "0..*" -- "1" Semester : Semester
            Kurs "0..*" -- "1" Modul : Modul
            KursBT "0..*" -- "1" Kurs : Kurs
            KursBT "0..*" -- "1" ModulBT : ModulBT
            KursBT "0..*" -- "1" Raum : Raum
            KursBT "0..*" -- "1" Lehrperson : Lehrperson
            KursBT "0..*" -- "1" Termin : Termin
            Belegung "0..*" -- "1" KursBT : KursBT
            Belegung "0..*" -- "1" StudentIn : StudentIn

            classDef entityStyle fill:#d0d0d0,stroke:#333,stroke-width:2px
        """
    ).strip()


def test_mermaid_relationships_render_as_direct_associations() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="Teacher", key="teacher_id"),
            Entity(entityname="Course", key="course_id"),
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
    )

    builder = MermaidClassDiagramTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
        ---
        classDiagram
            direction LR
            class Teacher:::entityStyle {
                **key**(teacher_id INTEGER)
            }
            class Course:::entityStyle {
                **key**(course_id INTEGER)
            }
            Teacher "1" -- "0..*" Course : Teaches

            classDef entityStyle fill:#d0d0d0,stroke:#333,stroke-width:2px
        """
    ).strip()


def test_mermaid_global_key_uses_role_when_present() -> None:
    er_schema = ERSchema(
        entities=[Entity(entityname="User", key="user_id")],
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    global_keys=[GlobalKey(targetentity="User", role="student")]
                ),
            )
        ],
    )

    builder = MermaidClassDiagramTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
        ---
        classDiagram
            direction LR
            class User:::entityStyle {
                **key**(user_id INTEGER)
            }
            class Enrollment {
                **global_key**(student)
            }
            Enrollment "0..*" -- "1" User : student

            classDef entityStyle fill:#d0d0d0,stroke:#333,stroke-width:2px
        """
    ).strip()
