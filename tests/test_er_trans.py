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
from edurel.syntax.rel_ast import RelAstFactory
from edurel.syntax.rel_yaml_schema import schema as rel_schema
from edurel.translation.er_trans import (
    ERSchemaTranslationBuilder,
    ERSchemaTranslationVisitor,
    MermaidTranslationBuilder,
    RelAstTranslationBuilder,
    YamlTranslationBuilder,
)
from edurel.utils.yaml import parse_yaml


def translate_er_ast_to_rel_ast(er_schema: ERSchema):
    builder = RelAstTranslationBuilder()
    visitor = ERSchemaTranslationVisitor(builder)
    visitor.visit(er_schema)
    return builder.build()


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

    builder = MermaidTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
          themeCSS: |
            .classLabel .box {
              fill: transparent !important;
              stroke: none !important;
              opacity: 0 !important;
            }
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

    builder = MermaidTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
          themeCSS: |
            .classLabel .box {
              fill: transparent !important;
              stroke: none !important;
              opacity: 0 !important;
            }
        ---
        classDiagram
            direction LR
            class Teacher:::entityStyle {
                **key**(teacher_id INTEGER)
            }
            class Course:::entityStyle {
                **key**(course_id INTEGER)
            }
            Teacher "1" -- "1..*" Course : Teaches

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

    builder = MermaidTranslationBuilder(direction="LR")
    visitor = ERSchemaTranslationVisitor(builder)

    visitor.visit(er_schema)

    assert builder.build() == dedent(
        """
        ---
        config:
          class:
            hideEmptyMembersBox: true
          themeCSS: |
            .classLabel .box {
              fill: transparent !important;
              stroke: none !important;
              opacity: 0 !important;
            }
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


def test_rel_ast_translation_builder_defaults_missing_keytype_to_integer() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(
                entityname="Author",
                key="AuthorID",
                attributes=[Attribute(attributename="Name", type="TEXT")],
            )
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Authorship",
                identification=Identification(
                    localkey="AuthorshipID",
                    global_keys=[GlobalKey(targetentity="Author", role="Writer")],
                ),
            )
        ],
    )

    assert translate_er_ast_to_rel_ast(er_schema) == RelAstFactory.create_schema(
        {
            "tables": [
                {
                    "tablename": "Author",
                    "columns": [
                        {"columnname": "AuthorID", "type": "INTEGER"},
                        {"columnname": "Name", "type": "TEXT"},
                    ],
                    "primary_key": ["AuthorID"],
                },
                {
                    "tablename": "Authorship",
                    "columns": [
                        {"columnname": "AuthorshipID", "type": "INTEGER"},
                        {"columnname": "WriterID", "type": "INTEGER"},
                    ],
                    "primary_key": ["AuthorshipID", "WriterID"],
                    "foreign_keys": [
                        {
                            "sourcecolumns": ["WriterID"],
                            "targettable": "Author",
                            "targetcolumns": ["AuthorID"],
                            "fkname": "fk_Authorship_Writer",
                        }
                    ],
                },
            ]
        }
    )


def test_rel_ast_translation_builder_creates_bridge_table_for_many_to_many_relationship() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="Student", key="StudentID", keytype="INTEGER"),
            Entity(entityname="Course", key="CourseID", keytype="INTEGER"),
        ],
        relationships=[
            Relationship(
                relationshipname="Enrollment",
                entities=[
                    RelationshipEntity(
                        entityname="Student",
                        role="Participant",
                        cardinality="MANY",
                    ),
                    RelationshipEntity(
                        entityname="Course",
                        role="Offering",
                        cardinality="MANY",
                    ),
                ],
                attributes=[Attribute(attributename="EnrolledOn", type="DATE")],
            )
        ],
    )

    builder = RelAstTranslationBuilder()
    ERSchemaTranslationVisitor(builder).visit(er_schema)

    assert builder.build() == RelAstFactory.create_schema(
        {
            "tables": [
                {
                    "tablename": "Student",
                    "columns": [{"columnname": "StudentID", "type": "INTEGER"}],
                    "primary_key": ["StudentID"],
                },
                {
                    "tablename": "Course",
                    "columns": [{"columnname": "CourseID", "type": "INTEGER"}],
                    "primary_key": ["CourseID"],
                },
                {
                    "tablename": "Enrollment",
                    "columns": [
                        {"columnname": "ParticipantID", "type": "INTEGER"},
                        {"columnname": "OfferingID", "type": "INTEGER"},
                        {"columnname": "EnrolledOn", "type": "DATE"},
                    ],
                    "primary_key": ["ParticipantID", "OfferingID"],
                    "foreign_keys": [
                        {
                            "sourcecolumns": ["ParticipantID"],
                            "targettable": "Student",
                            "targetcolumns": ["StudentID"],
                            "fkname": "fk_Enrollment_Participant",
                        },
                        {
                            "sourcecolumns": ["OfferingID"],
                            "targettable": "Course",
                            "targetcolumns": ["CourseID"],
                            "fkname": "fk_Enrollment_Offering",
                        },
                    ],
                },
            ]
        }
    )


def test_rel_ast_translation_builder_marks_direct_fk_nullable_for_optional_many_left_side() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="Book", key="BookID", keytype="INTEGER"),
            Entity(entityname="Publisher", key="PublisherID", keytype="INTEGER"),
        ],
        relationships=[
            Relationship(
                relationshipname="BookPublisher",
                entities=[
                    RelationshipEntity(
                        entityname="Book",
                        role="PublishedBook",
                        cardinality="OPTIONAL_MANY",
                    ),
                    RelationshipEntity(
                        entityname="Publisher",
                        role="BookPublisher",
                        cardinality="ONE",
                    ),
                ],
            )
        ],
    )

    assert translate_er_ast_to_rel_ast(er_schema) == RelAstFactory.create_schema(
        {
            "tables": [
                {
                    "tablename": "Book",
                    "columns": [
                        {"columnname": "BookID", "type": "INTEGER"},
                        {
                            "columnname": "BookPublisherID",
                            "type": "INTEGER",
                            "nullable": True,
                        },
                    ],
                    "primary_key": ["BookID"],
                    "foreign_keys": [
                        {
                            "sourcecolumns": ["BookPublisherID"],
                            "targettable": "Publisher",
                            "targetcolumns": ["PublisherID"],
                            "fkname": "fk_BookPublisher",
                        }
                    ],
                },
                {
                    "tablename": "Publisher",
                    "columns": [{"columnname": "PublisherID", "type": "INTEGER"}],
                    "primary_key": ["PublisherID"],
                },
            ]
        }
    )


def test_rel_ast_translation_builder_marks_direct_fk_nullable_for_optional_many_right_side() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="Book", key="BookID", keytype="INTEGER"),
            Entity(entityname="Publisher", key="PublisherID", keytype="INTEGER"),
        ],
        relationships=[
            Relationship(
                relationshipname="BookPublisher",
                entities=[
                    RelationshipEntity(
                        entityname="Publisher",
                        role="BookPublisher",
                        cardinality="ONE",
                    ),
                    RelationshipEntity(
                        entityname="Book",
                        role="PublishedBook",
                        cardinality="OPTIONAL_MANY",
                    ),
                ],
            )
        ],
    )

    assert translate_er_ast_to_rel_ast(er_schema) == RelAstFactory.create_schema(
        {
            "tables": [
                {
                    "tablename": "Book",
                    "columns": [
                        {"columnname": "BookID", "type": "INTEGER"},
                        {
                            "columnname": "BookPublisherID",
                            "type": "INTEGER",
                            "nullable": True,
                        },
                    ],
                    "primary_key": ["BookID"],
                    "foreign_keys": [
                        {
                            "sourcecolumns": ["BookPublisherID"],
                            "targettable": "Publisher",
                            "targetcolumns": ["PublisherID"],
                            "fkname": "fk_BookPublisher",
                        }
                    ],
                },
                {
                    "tablename": "Publisher",
                    "columns": [{"columnname": "PublisherID", "type": "INTEGER"}],
                    "primary_key": ["PublisherID"],
                },
            ]
        }
    )


def test_rel_ast_translation_builder_translates_library_er_schema_to_expected_rel_ast() -> None:
    er_yaml = dedent(
        """
        entities:
        - entityname: Book
          key: BookID
          keytype: INTEGER
          attributes:
          - attributename: ISBN
            type: TEXT
          - attributename: Title
            type: TEXT
          - attributename: PublicationYear
            type: INTEGER

        - entityname: Member
          key: MemberID
          keytype: INTEGER
          attributes:
          - attributename: FirstName
            type: TEXT
          - attributename: LastName
            type: TEXT
          - attributename: Email
            type: TEXT
          - attributename: Phone
            type: TEXT
            nullable: true
          - attributename: MembershipDate
            type: DATE

        - entityname: Student
          attributes:
          - attributename: StudentNumber
            type: TEXT
          - attributename: EnrollmentYear
            type: INTEGER
          - attributename: Program
            type: TEXT

        - entityname: Faculty
          attributes:
          - attributename: FacultyNumber
            type: TEXT
          - attributename: Department
            type: TEXT
          - attributename: Rank
            type: TEXT

        - entityname: Staff
          attributes:
          - attributename: StaffNumber
            type: TEXT
          - attributename: Position
            type: TEXT
          - attributename: HireDate
            type: DATE

        - entityname: Author
          key: AuthorID
          keytype: INTEGER
          attributes:
          - attributename: FirstName
            type: TEXT
          - attributename: LastName
            type: TEXT
          - attributename: Biography
            type: TEXT
            nullable: true

        - entityname: Publisher
          key: PublisherID
          keytype: INTEGER
          attributes:
          - attributename: Name
            type: TEXT
          - attributename: Address
            type: TEXT
            nullable: true
          - attributename: Website
            type: TEXT
            nullable: true

        - entityname: LibraryBranch
          key: LibraryBranchID
          keytype: INTEGER
          attributes:
          - attributename: Name
            type: TEXT
          - attributename: Address
            type: TEXT
          - attributename: Phone
            type: TEXT

        - entityname: Subject
          key: SubjectID
          keytype: INTEGER
          attributes:
          - attributename: Name
            type: TEXT
          - attributename: Description
            type: TEXT
            nullable: true

        associative_entities:
        - associationname: BookCopy
          identification:
            localkey: BookCopyID
            keytype: INTEGER
            global:
            - targetentity: Book
              role: Book
          associations:
          - targetentity: LibraryBranch
            role: HousingBranch
            cardinality: ONE
          attributes:
          - attributename: Barcode
            type: TEXT
          - attributename: AcquisitionDate
            type: DATE

        - associationname: Loan
          identification:
            localkey: LoanID
            keytype: INTEGER
          associations:
          - targetentity: BookCopy
            role: BorrowedCopy
            cardinality: ONE
          - targetentity: Member
            role: Borrower
            cardinality: ONE
          attributes:
          - attributename: CheckoutDate
            type: DATE
          - attributename: DueDate
            type: DATE
          - attributename: ReturnDate
            type: DATE
            nullable: true
          - attributename: RenewalCount
            type: INTEGER

        - associationname: Reservation
          identification:
            localkey: ReservationID
            keytype: INTEGER
          associations:
          - targetentity: Book
            role: ReservedBook
            cardinality: ONE
          - targetentity: Member
            role: Requester
            cardinality: ONE
          attributes:
          - attributename: ReservationDate
            type: DATE
          - attributename: ExpirationDate
            type: DATE
          - attributename: NotificationDate
            type: DATE
            nullable: true

        - associationname: Fine
          identification:
            localkey: FineID
            keytype: INTEGER
          associations:
          - targetentity: Loan
            role: OverdueLoan
            cardinality: ONE
          - targetentity: Member
            role: FinedMember
            cardinality: ONE
          attributes:
          - attributename: Amount
            type: DECIMAL
          - attributename: AssessmentDate
            type: DATE
          - attributename: PaymentDate
            type: DATE
            nullable: true
          - attributename: Reason
            type: TEXT

        - associationname: BookAuthorship
          identification:
            global:
            - targetentity: Book
              role: AuthoredBook
            - targetentity: Author
              role: BookAuthor
          attributes:
          - attributename: AuthorOrder
            type: INTEGER

        - associationname: BookSubject
          identification:
            global:
            - targetentity: Book
              role: ClassifiedBook
            - targetentity: Subject
              role: Classification
          attributes:
          - attributename: IsPrimary
            type: INTEGER

        relationships:
        - relationshipname: BookPublisher
          entities:
          - targetentity: Book
            role: PublishedBook
            cardinality: MANY
          - targetentity: Publisher
            role: BookPublisher
            cardinality: ONE

        - relationshipname: MemberHomeBranch
          entities:
          - targetentity: Member
            role: BranchMember
            cardinality: MANY
          - targetentity: LibraryBranch
            role: HomeBranch
            cardinality: ONE

        inheritances:
        - superentity: Member
          subentities:
          - Student
          - Faculty
          - Staff

        valuelists:
        - valuelistname: LoanStatus
          values:
          - Active
          - Returned
          - Overdue
          - Lost
          - Renewed
          many_to_one_from_entities:
          - sourceentity: Loan

        - valuelistname: CopyCondition
          values:
          - New
          - Good
          - Fair
          - Poor
          - Damaged
          - Withdrawn
          many_to_one_from_entities:
          - sourceentity: BookCopy

        - valuelistname: ReservationStatus
          values:
          - Pending
          - ReadyForPickup
          - Fulfilled
          - Cancelled
          - Expired
          many_to_one_from_entities:
          - sourceentity: Reservation

        - valuelistname: MemberStatus
          values:
          - Active
          - Suspended
          - Expired
          - Blocked
          many_to_one_from_entities:
          - sourceentity: Member

        - valuelistname: FineStatus
          values:
          - Outstanding
          - Paid
          - Waived
          - InCollection
          many_to_one_from_entities:
          - sourceentity: Fine

        - valuelistname: AuthorRole
          values:
          - PrimaryAuthor
          - CoAuthor
          - Editor
          - Translator
          - Illustrator
          many_to_one_from_entities:
          - sourceentity: BookAuthorship

        - valuelistname: MediaFormat
          values:
          - Hardcover
          - Paperback
          - EBook
          - Audiobook
          - DVD
          - CDROM
          many_to_one_from_entities:
          - sourceentity: Book
        """
    )

    rel_yaml = dedent(
        """
        tables:
        - tablename: Book
          columns:
          - columnname: BookID
            type: INTEGER
          - columnname: ISBN
            type: TEXT
          - columnname: Title
            type: TEXT
          - columnname: PublicationYear
            type: INTEGER
          - columnname: BookPublisherID
            type: INTEGER
          - columnname: MediaFormatID
            type: INTEGER
          primary_key:
          - BookID
          foreign_keys:
          - sourcecolumns:
            - BookPublisherID
            targettable: Publisher
            targetcolumns:
            - PublisherID
            fkname: fk_BookPublisher
          - sourcecolumns:
            - MediaFormatID
            targettable: MediaFormat
            targetcolumns:
            - ID
            fkname: fk_Book_MediaFormat
        - tablename: Member
          columns:
          - columnname: MemberID
            type: INTEGER
          - columnname: FirstName
            type: TEXT
          - columnname: LastName
            type: TEXT
          - columnname: Email
            type: TEXT
          - columnname: Phone
            type: TEXT
            nullable: true
          - columnname: MembershipDate
            type: DATE
          - columnname: HomeBranchID
            type: INTEGER
          - columnname: MemberStatusID
            type: INTEGER
          primary_key:
          - MemberID
          foreign_keys:
          - sourcecolumns:
            - HomeBranchID
            targettable: LibraryBranch
            targetcolumns:
            - LibraryBranchID
            fkname: fk_MemberHomeBranch
          - sourcecolumns:
            - MemberStatusID
            targettable: MemberStatus
            targetcolumns:
            - ID
            fkname: fk_Member_MemberStatus
        - tablename: Student
          columns:
          - columnname: MemberID
            type: INTEGER
          - columnname: StudentNumber
            type: TEXT
          - columnname: EnrollmentYear
            type: INTEGER
          - columnname: Program
            type: TEXT
          primary_key:
          - MemberID
          foreign_keys:
          - sourcecolumns:
            - MemberID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Student_Member
        - tablename: Faculty
          columns:
          - columnname: MemberID
            type: INTEGER
          - columnname: FacultyNumber
            type: TEXT
          - columnname: Department
            type: TEXT
          - columnname: Rank
            type: TEXT
          primary_key:
          - MemberID
          foreign_keys:
          - sourcecolumns:
            - MemberID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Faculty_Member
        - tablename: Staff
          columns:
          - columnname: MemberID
            type: INTEGER
          - columnname: StaffNumber
            type: TEXT
          - columnname: Position
            type: TEXT
          - columnname: HireDate
            type: DATE
          primary_key:
          - MemberID
          foreign_keys:
          - sourcecolumns:
            - MemberID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Staff_Member
        - tablename: Author
          columns:
          - columnname: AuthorID
            type: INTEGER
          - columnname: FirstName
            type: TEXT
          - columnname: LastName
            type: TEXT
          - columnname: Biography
            type: TEXT
            nullable: true
          primary_key:
          - AuthorID
        - tablename: Publisher
          columns:
          - columnname: PublisherID
            type: INTEGER
          - columnname: Name
            type: TEXT
          - columnname: Address
            type: TEXT
            nullable: true
          - columnname: Website
            type: TEXT
            nullable: true
          primary_key:
          - PublisherID
        - tablename: LibraryBranch
          columns:
          - columnname: LibraryBranchID
            type: INTEGER
          - columnname: Name
            type: TEXT
          - columnname: Address
            type: TEXT
          - columnname: Phone
            type: TEXT
          primary_key:
          - LibraryBranchID
        - tablename: Subject
          columns:
          - columnname: SubjectID
            type: INTEGER
          - columnname: Name
            type: TEXT
          - columnname: Description
            type: TEXT
            nullable: true
          primary_key:
          - SubjectID
        - tablename: LoanStatus
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: CopyCondition
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: ReservationStatus
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: MemberStatus
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: FineStatus
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: AuthorRole
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: MediaFormat
          columns:
          - columnname: ID
            type: INTEGER
          - columnname: Description
            type: TEXT
          - columnname: IsValid
            type: INTEGER
          - columnname: SortOrder
            type: INTEGER
          primary_key:
          - ID
        - tablename: BookCopy
          columns:
          - columnname: BookCopyID
            type: INTEGER
          - columnname: BookID
            type: INTEGER
          - columnname: Barcode
            type: TEXT
          - columnname: AcquisitionDate
            type: DATE
          - columnname: HousingBranchID
            type: INTEGER
          - columnname: CopyConditionID
            type: INTEGER
          primary_key:
          - BookCopyID
          - BookID
          foreign_keys:
          - sourcecolumns:
            - BookID
            targettable: Book
            targetcolumns:
            - BookID
            fkname: fk_BookCopy_Book
          - sourcecolumns:
            - HousingBranchID
            targettable: LibraryBranch
            targetcolumns:
            - LibraryBranchID
            fkname: fk_BookCopy_HousingBranch_assoc
          - sourcecolumns:
            - CopyConditionID
            targettable: CopyCondition
            targetcolumns:
            - ID
            fkname: fk_BookCopy_CopyCondition
        - tablename: Loan
          columns:
          - columnname: LoanID
            type: INTEGER
          - columnname: CheckoutDate
            type: DATE
          - columnname: DueDate
            type: DATE
          - columnname: ReturnDate
            type: DATE
            nullable: true
          - columnname: RenewalCount
            type: INTEGER
          - columnname: BookCopyID
            type: INTEGER
          - columnname: BookID
            type: INTEGER
          - columnname: BorrowerID
            type: INTEGER
          - columnname: LoanStatusID
            type: INTEGER
          primary_key:
          - LoanID
          foreign_keys:
          - sourcecolumns:
            - BookCopyID
            - BookID
            targettable: BookCopy
            targetcolumns:
            - BookCopyID
            - BookID
            fkname: fk_Loan_BorrowedCopy_assoc
          - sourcecolumns:
            - BorrowerID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Loan_Borrower_assoc
          - sourcecolumns:
            - LoanStatusID
            targettable: LoanStatus
            targetcolumns:
            - ID
            fkname: fk_Loan_LoanStatus
        - tablename: Reservation
          columns:
          - columnname: ReservationID
            type: INTEGER
          - columnname: ReservationDate
            type: DATE
          - columnname: ExpirationDate
            type: DATE
          - columnname: NotificationDate
            type: DATE
            nullable: true
          - columnname: ReservedBookID
            type: INTEGER
          - columnname: RequesterID
            type: INTEGER
          - columnname: ReservationStatusID
            type: INTEGER
          primary_key:
          - ReservationID
          foreign_keys:
          - sourcecolumns:
            - ReservedBookID
            targettable: Book
            targetcolumns:
            - BookID
            fkname: fk_Reservation_ReservedBook_assoc
          - sourcecolumns:
            - RequesterID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Reservation_Requester_assoc
          - sourcecolumns:
            - ReservationStatusID
            targettable: ReservationStatus
            targetcolumns:
            - ID
            fkname: fk_Reservation_ReservationStatus
        - tablename: Fine
          columns:
          - columnname: FineID
            type: INTEGER
          - columnname: Amount
            type: DECIMAL
          - columnname: AssessmentDate
            type: DATE
          - columnname: PaymentDate
            type: DATE
            nullable: true
          - columnname: Reason
            type: TEXT
          - columnname: OverdueLoanID
            type: INTEGER
          - columnname: FinedMemberID
            type: INTEGER
          - columnname: FineStatusID
            type: INTEGER
          primary_key:
          - FineID
          foreign_keys:
          - sourcecolumns:
            - OverdueLoanID
            targettable: Loan
            targetcolumns:
            - LoanID
            fkname: fk_Fine_OverdueLoan_assoc
          - sourcecolumns:
            - FinedMemberID
            targettable: Member
            targetcolumns:
            - MemberID
            fkname: fk_Fine_FinedMember_assoc
          - sourcecolumns:
            - FineStatusID
            targettable: FineStatus
            targetcolumns:
            - ID
            fkname: fk_Fine_FineStatus
        - tablename: BookAuthorship
          columns:
          - columnname: AuthoredBookID
            type: INTEGER
          - columnname: BookAuthorID
            type: INTEGER
          - columnname: AuthorOrder
            type: INTEGER
          - columnname: AuthorRoleID
            type: INTEGER
          primary_key:
          - AuthoredBookID
          - BookAuthorID
          foreign_keys:
          - sourcecolumns:
            - AuthoredBookID
            targettable: Book
            targetcolumns:
            - BookID
            fkname: fk_BookAuthorship_AuthoredBook
          - sourcecolumns:
            - BookAuthorID
            targettable: Author
            targetcolumns:
            - AuthorID
            fkname: fk_BookAuthorship_BookAuthor
          - sourcecolumns:
            - AuthorRoleID
            targettable: AuthorRole
            targetcolumns:
            - ID
            fkname: fk_BookAuthorship_AuthorRole
        - tablename: BookSubject
          columns:
          - columnname: ClassifiedBookID
            type: INTEGER
          - columnname: ClassificationID
            type: INTEGER
          - columnname: IsPrimary
            type: INTEGER
          primary_key:
          - ClassifiedBookID
          - ClassificationID
          foreign_keys:
          - sourcecolumns:
            - ClassifiedBookID
            targettable: Book
            targetcolumns:
            - BookID
            fkname: fk_BookSubject_ClassifiedBook
          - sourcecolumns:
            - ClassificationID
            targettable: Subject
            targetcolumns:
            - SubjectID
            fkname: fk_BookSubject_Classification
        datalists:
        - tablename: LoanStatus
          values:
          - Active
          - Returned
          - Overdue
          - Lost
          - Renewed
        - tablename: CopyCondition
          values:
          - New
          - Good
          - Fair
          - Poor
          - Damaged
          - Withdrawn
        - tablename: ReservationStatus
          values:
          - Pending
          - ReadyForPickup
          - Fulfilled
          - Cancelled
          - Expired
        - tablename: MemberStatus
          values:
          - Active
          - Suspended
          - Expired
          - Blocked
        - tablename: FineStatus
          values:
          - Outstanding
          - Paid
          - Waived
          - InCollection
        - tablename: AuthorRole
          values:
          - PrimaryAuthor
          - CoAuthor
          - Editor
          - Translator
          - Illustrator
        - tablename: MediaFormat
          values:
          - Hardcover
          - Paperback
          - EBook
          - Audiobook
          - DVD
          - CDROM
        """
    )

    er_schema = ERAstFactory.create_schema(parse_yaml(er_yaml, schema))
    expected_rel_schema = RelAstFactory.create_schema(parse_yaml(rel_yaml, rel_schema))

    assert translate_er_ast_to_rel_ast(er_schema) == expected_rel_schema
