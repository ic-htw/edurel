from textwrap import dedent

from edurel.syntax.er_ast import (
    Association,
    AssociativeEntity,
    Attribute,
    Entity,
    ERAstFactory,
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
from edurel.utils.yaml import parse_yaml


def test_parse_builds_er_ast_from_valid_yaml() -> None:
    text = dedent(
        """
        entities:
        - entityname: Student
          key: StudentID
          keytype: INTEGER
          attributes:
          - attributename: Name
            type: TEXT
          - attributename: GPA
            type: DECIMAL(3,2)
            nullable: true
        associative_entities:
        - associationname: Enrollment
          identification:
            localkey: EnrollmentID
            keytype: INTEGER
            global:
            - targetentity: Student
              role: enrollee
          associations:
          - targetentity: Course
            role: chosen_course
            cardinality: MANY
          attributes:
          - attributename: EnrolledOn
            type: DATE
        relationships:
        - relationshipname: Advises
          entities:
          - entityname: Teacher
            role: advisor
            cardinality: ONE
          - entityname: Student
            role: advisee
            cardinality: OPTIONAL_MANY
          attributes:
          - attributename: Since
            type: DATE
        inheritances:
        - superentity: Person
          subentities:
          - Student
          - Teacher
          implementation: ONE_TABLE_PER_ENTITY
        valuelists:
        - valuelistname: Grade
          values:
          - A
          - B
          - C
          many_to_one_from_entities:
          - entityname: Enrollment
        """
    )

    assert ERAstFactory.create_schema(parse_yaml(text, schema)) == ERSchema(
        entities=[
            Entity(
                entityname="Student",
                key="StudentID",
                keytype="INTEGER",
                attributes=[
                    Attribute(attributename="Name", type="TEXT"),
                    Attribute(
                        attributename="GPA",
                        type="DECIMAL(3,2)",
                        nullable=True,
                    ),
                ],
            )
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    localkey="EnrollmentID",
                    keytype="INTEGER",
                    global_keys=[
                        GlobalKey(targetentity="Student", role="enrollee"),
                    ],
                ),
                associations=[
                    Association(
                        targetentity="Course",
                        role="chosen_course",
                        cardinality="MANY",
                    )
                ],
                attributes=[Attribute(attributename="EnrolledOn", type="DATE")],
            )
        ],
        relationships=[
            Relationship(
                relationshipname="Advises",
                entities=[
                    RelationshipEntity(
                        entityname="Teacher",
                        role="advisor",
                        cardinality="ONE",
                    ),
                    RelationshipEntity(
                        entityname="Student",
                        role="advisee",
                        cardinality="OPTIONAL_MANY",
                    ),
                ],
                attributes=[Attribute(attributename="Since", type="DATE")],
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
                valuelistname="Grade",
                values=["A", "B", "C"],
                many_to_one_from_entities=[
                    ManyToOneEntity(entityname="Enrollment"),
                ],
            )
        ],
    )


def test_parse_builds_er_ast_with_omitted_optional_fields() -> None:
    text = dedent(
        """
        entities:
        - entityname: Student
        associative_entities:
        - associationname: Enrollment
        relationships:
        - relationshipname: Knows
          entities:
          - entityname: Student
          - entityname: Teacher
        inheritances:
        - superentity: Person
          subentities:
          - Student
        valuelists:
        - valuelistname: Status
          values:
          - active
          - inactive
        """
    )

    assert ERAstFactory.create_schema(parse_yaml(text, schema)) == ERSchema(
        entities=[Entity(entityname="Student")],
        associative_entities=[AssociativeEntity(associationname="Enrollment")],
        relationships=[
            Relationship(
                relationshipname="Knows",
                entities=[
                    RelationshipEntity(entityname="Student"),
                    RelationshipEntity(entityname="Teacher"),
                ],
            )
        ],
        inheritances=[
            Inheritance(superentity="Person", subentities=["Student"]),
        ],
        valuelists=[
            ValueList(valuelistname="Status", values=["active", "inactive"]),
        ],
    )


def test_parse_builds_er_ast_with_identification_without_localkey() -> None:
    text = dedent(
        """
        associative_entities:
        - associationname: Enrollment
          identification:
            global:
            - targetentity: Student
              role: enrollee
          associations:
          - targetentity: Course
        """
    )

    assert ERAstFactory.create_schema(parse_yaml(text, schema)) == ERSchema(
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    global_keys=[
                        GlobalKey(targetentity="Student", role="enrollee"),
                    ]
                ),
                associations=[Association(targetentity="Course")],
            )
        ]
    )


def test_create_schema_returns_empty_er_schema_for_empty_input() -> None:
    assert ERAstFactory.create_schema({}) == ERSchema()
