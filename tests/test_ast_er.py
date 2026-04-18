from textwrap import dedent

import pytest

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
    validate_ast,
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
          - targetentity: Teacher
            role: advisor
            cardinality: ONE
          - targetentity: Student
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
          - sourceentity: Enrollment
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
          - targetentity: Student
          - targetentity: Teacher
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


def test_validate_ast_accepts_valid_er_schema() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="Person", key="PersonID"),
            Entity(entityname="Student"),
            Entity(entityname="Course", key="CourseID"),
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Enrollment",
                identification=Identification(
                    localkey="EnrollmentID",
                    global_keys=[GlobalKey(targetentity="Student")],
                ),
                associations=[Association(targetentity="Course")],
            )
        ],
        relationships=[
            Relationship(
                relationshipname="Takes",
                entities=[
                    RelationshipEntity(entityname="Student"),
                    RelationshipEntity(entityname="Course"),
                ],
            )
        ],
        inheritances=[
            Inheritance(superentity="Person", subentities=["Student"]),
        ],
        valuelists=[
            ValueList(
                valuelistname="Status",
                values=["active", "inactive"],
                many_to_one_from_entities=[ManyToOneEntity(entityname="Enrollment")],
            )
        ],
    )

    assert validate_ast(er_schema) is None

def test_validate_ast_reports_requested_semantic_errors() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(
                entityname="Shared",
                key="SharedID",
                attributes=[
                    Attribute(attributename="Name", type="TEXT"),
                    Attribute(attributename="Name", type="TEXT"),
                ],
            ),
            Entity(entityname="Shared", key="OtherID"),
            Entity(entityname="NoKey"),
            Entity(entityname="Leaf", key="LeafID"),
            Entity(entityname="OnlyEntity"),
            Entity(entityname="Root", key="RootID"),
            Entity(entityname="OtherRoot", key="OtherRootID"),
        ],
        associative_entities=[
            AssociativeEntity(
                associationname="Shared",
                identification=Identification(localkey="SharedAssocID"),
            ),
            AssociativeEntity(
                associationname="Join",
                attributes=[
                    Attribute(attributename="Note", type="TEXT"),
                    Attribute(attributename="Note", type="TEXT"),
                ],
            ),
            AssociativeEntity(associationname="Join"),
            AssociativeEntity(
                associationname="ConflictAssoc",
                identification=Identification(
                    global_keys=[
                        GlobalKey(targetentity="Shared"),
                        GlobalKey(targetentity="Ghost"),
                    ]
                ),
                associations=[
                    Association(targetentity="Shared"),
                    Association(targetentity="Ghost"),
                ],
            ),
            AssociativeEntity(
                associationname="EmptyId",
                identification=Identification(),
            ),
            AssociativeEntity(
                associationname="SubAssoc",
                identification=Identification(localkey="SubAssocID"),
            ),
            AssociativeEntity(
                associationname="AssocSuper",
                identification=Identification(localkey="AssocSuperID"),
            ),
        ],
        relationships=[
            Relationship(
                relationshipname="Rel",
                entities=[RelationshipEntity(entityname="Ghost")],
                attributes=[
                    Attribute(attributename="Since", type="DATE"),
                    Attribute(attributename="Since", type="DATE"),
                ],
            ),
            Relationship(
                relationshipname="Rel",
                entities=[
                    RelationshipEntity(entityname="Shared"),
                    RelationshipEntity(entityname="Join"),
                ],
            ),
        ],
        inheritances=[
            Inheritance(superentity="Root", subentities=["Leaf", "Leaf"]),
            Inheritance(superentity="OtherRoot", subentities=["Leaf"]),
            Inheritance(superentity="BridgeGhost", subentities=["Phantom"]),
            Inheritance(superentity="Shared", subentities=["SubAssoc"]),
            Inheritance(superentity="AssocSuper", subentities=["OnlyEntity"]),
        ],
        valuelists=[
            ValueList(
                valuelistname="Shared",
                values=["active", "active"],
                many_to_one_from_entities=[
                    ManyToOneEntity(entityname="Join"),
                    ManyToOneEntity(entityname="Join"),
                    ManyToOneEntity(entityname="Ghost"),
                ],
            ),
            ValueList(valuelistname="Shared", values=["inactive"]),
        ],
    )

    with pytest.raises(ValueError) as exc_info:
        validate_ast(er_schema)

    message = str(exc_info.value)
    assert "AST validation failed:" in message
    assert "Duplicate entityname 'Shared'." in message
    assert "Duplicate associationname 'Join'." in message
    assert "Duplicate relationshipname 'Rel'." in message
    assert "Duplicate valuelistname 'Shared'." in message
    assert "Entity 'Shared' has duplicate attributename 'Name'." in message
    assert "Associative entity 'Join' has duplicate attributename 'Note'." in message
    assert "Relationship 'Rel' has duplicate attributename 'Since'." in message
    assert "Valuelist 'Shared' has duplicate value 'active'." in message
    assert "Valuelist 'Shared' has duplicate sourceentity 'Join'." in message
    assert "Inheritance superentity 'Root' has duplicate subentity 'Leaf'." in message
    assert (
        "Name 'Shared' must not be used as both entityname and associationname."
        in message
    )
    assert (
        "Name 'Shared' must not be used as both entityname and valuelistname."
        in message
    )
    assert (
        "Name 'Shared' must not be used as both associationname and valuelistname."
        in message
    )
    assert (
        "Associative entity 'ConflictAssoc' targetentity 'Shared' must not appear "
        "in both identification_schema and association_schema."
        in message
    )
    assert "Inheritance superentity 'BridgeGhost' does not exist" in message
    assert "Inheritance subentity 'Phantom' does not exist" in message
    assert "Valuelist 'Shared' sourceentity 'Ghost' does not exist" in message
    assert (
        "Associative entity 'ConflictAssoc' identification targetentity 'Ghost' "
        "does not exist"
        in message
    )
    assert (
        "Associative entity 'ConflictAssoc' association targetentity 'Ghost' "
        "does not exist"
        in message
    )
    assert "Relationship 'Rel' targetentity 'Ghost' does not exist" in message
    assert "Entity 'NoKey' is not a subentity and must have a key." in message
    assert "Entity 'Leaf' is a subentity and must not have a key." in message
    assert (
        "Associative entity 'Join' is not a subentity and must have an "
        "identification section."
        in message
    )
    assert (
        "Associative entity 'SubAssoc' is a subentity and must not have an "
        "identification section."
        in message
    )
    assert (
        "Associative entity 'EmptyId' identification_schema must define localkey "
        "or global."
        in message
    )
    assert "Relationship 'Rel' must have exactly two entities." in message
    assert (
        "Subentity 'Leaf' cannot have multiple superentities: OtherRoot, Root."
        in message
    )
    assert (
        "Inheritance superentity 'AssocSuper' is an associative entity, so "
        "subentity 'OnlyEntity' must also be an associative entity."
        in message
    )


def test_validate_ast_reports_inheritance_cycles() -> None:
    er_schema = ERSchema(
        entities=[
            Entity(entityname="A"),
            Entity(entityname="B"),
            Entity(entityname="C", key="CID"),
        ],
        inheritances=[
            Inheritance(superentity="A", subentities=["B"]),
            Inheritance(superentity="B", subentities=["A"]),
            Inheritance(superentity="C", subentities=["C"]),
        ],
    )

    with pytest.raises(ValueError) as exc_info:
        validate_ast(er_schema)

    message = str(exc_info.value)
    assert "Inheritance cycle detected involving 'A'." in message
    assert "Inheritance cycle detected involving 'C'." in message
