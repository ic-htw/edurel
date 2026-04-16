import pytest
from textwrap import dedent

from edurel.syntax.er_yaml_schema import schema
from edurel.utils.yaml import parse_yaml


def test_parse_yaml_accepts_complete_valid_er_document() -> None:
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

    assert parse_yaml(text, schema) == {
        "entities": [
            {
                "entityname": "Student",
                "key": "StudentID",
                "keytype": "INTEGER",
                "attributes": [
                    {"attributename": "Name", "type": "TEXT"},
                    {
                        "attributename": "GPA",
                        "type": "DECIMAL(3,2)",
                        "nullable": True,
                    },
                ],
            }
        ],
        "associative_entities": [
            {
                "associationname": "Enrollment",
                "identification": {
                    "localkey": "EnrollmentID",
                    "keytype": "INTEGER",
                    "global": [{"targetentity": "Student", "role": "enrollee"}],
                },
                "associations": [
                    {
                        "targetentity": "Course",
                        "role": "chosen_course",
                        "cardinality": "MANY",
                    }
                ],
                "attributes": [{"attributename": "EnrolledOn", "type": "DATE"}],
            }
        ],
        "relationships": [
            {
                "relationshipname": "Advises",
                "entities": [
                    {
                        "entityname": "Teacher",
                        "role": "advisor",
                        "cardinality": "ONE",
                    },
                    {
                        "entityname": "Student",
                        "role": "advisee",
                        "cardinality": "OPTIONAL_MANY",
                    },
                ],
                "attributes": [{"attributename": "Since", "type": "DATE"}],
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
                "valuelistname": "Grade",
                "values": ["A", "B", "C"],
                "many_to_one_from_entities": [{"entityname": "Enrollment"}],
            }
        ],
    }


def test_parse_yaml_allows_omitted_optional_er_fields() -> None:
    text = dedent(
        """
        entities:
        - entityname: Student
          attributes:
          - attributename: Name
            type: TEXT
        associative_entities:
        - associationname: Enrollment
          associations:
          - targetentity: Student
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

    assert parse_yaml(text, schema) == {
        "entities": [
            {
                "entityname": "Student",
                "attributes": [{"attributename": "Name", "type": "TEXT"}],
            }
        ],
        "associative_entities": [
            {
                "associationname": "Enrollment",
                "associations": [{"targetentity": "Student"}],
            }
        ],
        "relationships": [
            {
                "relationshipname": "Knows",
                "entities": [{"entityname": "Student"}, {"entityname": "Teacher"}],
            }
        ],
        "inheritances": [{"superentity": "Person", "subentities": ["Student"]}],
        "valuelists": [
            {"valuelistname": "Status", "values": ["active", "inactive"]}
        ],
    }


def test_parse_yaml_allows_identification_without_localkey() -> None:
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

    assert parse_yaml(text, schema) == {
        "associative_entities": [
            {
                "associationname": "Enrollment",
                "identification": {
                    "global": [{"targetentity": "Student", "role": "enrollee"}],
                },
                "associations": [{"targetentity": "Course"}],
            }
        ]
    }


@pytest.mark.parametrize(
    "attribute_type",
    [
        "DECIMAL(9, 2)",
        "DECIMAL( 9,2)",
        "DECIMAL(9 , 2 )",
    ],
)
def test_parse_yaml_accepts_attribute_type_values_with_spaces(
    attribute_type: str,
) -> None:
    text = dedent(
        f"""
        entities:
        - entityname: Student
          attributes:
          - attributename: Score
            type: {attribute_type}
        """
    )

    assert parse_yaml(text, schema) == {
        "entities": [
            {
                "entityname": "Student",
                "attributes": [
                    {"attributename": "Score", "type": attribute_type},
                ],
            }
        ]
    }


@pytest.mark.parametrize(
    "attribute_type",
    [
        "INTEGER()",
        "VARCHAR(abc)",
        "TEXT()",
        "DECIMAL(9,2,1)",
    ],
)
def test_parse_yaml_rejects_invalid_attribute_type_values(attribute_type: str) -> None:
    text = dedent(
        f"""
        entities:
        - entityname: Student
          attributes:
          - attributename: Score
            type: {attribute_type}
        """
    )

    with pytest.raises(ValueError, match="YAML validation failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "found non-matching string" in message or "when expecting string matching" in message
    assert "Check the field format against the schema." in message


def test_parse_yaml_rejects_invalid_cardinality() -> None:
    text = dedent(
        """
        relationships:
        - relationshipname: Advises
          entities:
          - entityname: Teacher
            cardinality: ZERO_OR_ONE
          - entityname: Student
            cardinality: MANY
        """
    )

    with pytest.raises(ValueError, match="YAML validation failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "found non-matching string" in message or "when expecting string matching" in message
    assert "Check the field format against the schema." in message


def test_parse_yaml_reports_schema_error_with_fix() -> None:
    text = dedent(
        """
        entities:
        - entityname: Student
          attributes:
          - attributename: Name
            nullable: false
        """
    )

    with pytest.raises(ValueError, match="YAML validation failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "required key(s) 'type' not found" in message
    assert "Add the missing required field" in message


def test_parse_yaml_reports_malformed_yaml_with_fix() -> None:
    text = dedent(
        """
        relationships:
        - relationshipname: Advises
          entities:
            - entityname: Teacher
             cardinality: ONE
        """
    )

    with pytest.raises(ValueError, match="YAML parsing failed\\.") as exc_info:
        parse_yaml(text, schema)

    message = str(exc_info.value)
    assert "expected <block end>" in message
    assert "indentation" in message
