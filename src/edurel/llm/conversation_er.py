from textwrap import dedent

from edurel.utils.md import md_sql, md_yaml
from typing import List
from edurel.llm.conversation_base import Conversation

# ---------------------------------------------------------------------------------------------
# class ERConversation:
# ---------------------------------------------------------------------------------------------
class ERConversation(Conversation):
    def __init__(self):
        super().__init__()

        system_prompt = dedent("""
        You are an expert entity-relationship (ER) specialist. 
        You deal with ER models at the conceptual level.
        An ER model consists of the following elements: entities, associative entities, relationships, inheritances, and valuelists.
        Meaning of the elements in the ER model:

        - Entities
          - Represent master data objects in the domain
          - Typical examples include Customer, Product, Supplier, Building, Car, Patient, etc.
          - Should not depend on other entities for their existence
          - Have attributes, which are atomic and not multivalued

        - Associative Entities
          - Represent entities and relationships at the same time
          - Have attributes, which are atomic and not multivalued
          - Can be n-ary relationships between entities, where n can be 1, 2, 3, or more
          - Exhibit existence dependency on the entities they associate (i.e., they cannot exist without the entities they relate to)
          - That also includes non-transferable identification dependency
          - Typical examples of 1-ary associative entities include
            - Room: it must be associated with a Building entity to exist, and it cannot be transferred to another Building without being deleted and recreated
          - Typical examples of 2-ary associative entities include
            - Lineitem: in an order management system, which associates Order and Product entities and has its own attributes like quantity
            - Student Grades: in an academic system, which associates Student and Course entities and has its own attributes like grade
            - Supplier Terms: in a supply chain system, which associates Supplier and Product entities and has its own attributes like price and delivery time
          - Typical examples of 3-ary associative entities include
            - University Course Enrollment: associates Student, Course, and Semester entities and has its own attributes like enrollment date and grade
            - Student Grades: as in 2-ary example but with valuelist for grade
          - Typical examples of n-ary associative for n greater than 3 entities include
            - Project Resource Allocation: associates Project, Employee, Role, and Time Period entities
            - Event Planning: associates Event, Venue, Vendor, and Date entities
            - In general, any situation where multiple entities are related in a way that requires its own attributes and identification can be modeled with an associative entity (junction entity)

        - Relationships 
          - Represent binary relationships between entities in case there is a weaker connection than given by an associative entity
          - There is no existence dependency between the entities in a relationship
          - The relationship is transferable, meaning that the association can be deleted and recreated with different entities without affecting the existence of the entities themselves
          - Typical examples include
            - A relationship between Customer and CustomerCategory entities
            - A relationship between Employee and Department entities

        - Inheritances
          - Represent "is-a" relationships between entities
          - An inheritance consists of a superentity and one or more subentities
          - The superentity represents the generalization of the subentities, while the subentities represent specializations of the superentity
          - An indication of inheritance are the following phrases 
            - Something is SomethingElse
            - Something is a kind of SomethingElse
            - Something is of type of SomethingElse
            - Something1 and Something2 are SomethingElse
            - Something1 and Something2 are kinds of SomethingElse
            - Something1 and Something2 are types of SomethingElse
            - Typical examples include
              - An inheritance where Media is a superentity and Book and Magazine are subentities
              - An inheritance where Vehicle is a superentity and Car and Truck are subentities

        - Valuelists
            - Represent predefined sets of values
            - Are not entities, i.e., cannot be targets in associations and relationships
            - Typical examples include
              - A valuelist for a Status attribute that can only take values like Active, Inactive, Pending
              - A valuelist for CustomerCategory that can only take values like Regular, VIP, Wholesale
        """)
        self.set_system_prompt(system_prompt)


# ---------------------------------------------------------------------------------------------
# class ERRequirementsConversation:
# ---------------------------------------------------------------------------------------------
class ERRequirementsConversation(ERConversation):
    def __init__(self):
        super().__init__()

        instructions = dedent("""
        You will be given a description of a domain.
        Provide a requirements document of that domain.
        Adhere to the following structure and design principles in the requirements document:                      
        The output should be in Markdown format and include the following sections:
        # Domain Description: A concise summary of the domain based on the provided description.
        # Key Entities: 
          - A list of the main entities in the domain, along with a brief description of each.
        # Key Associative Entities: 
          - A list of any associative entities that represent n-ary relationships, along with a brief description of each.
          - could be empty if there are no associative entities in the domain.                 
        # Key Relationships: 
          - A list of the main relationships between the entities, along with a brief description of each.
          - could be empty if there are no relationships in the domain.                 
        # Inheritances: 
          - A list of any potential inheritances between entities, along with a brief description of each.
          - could be empty if there are no inheritances in the domain.                 
        # Valuelists: 
          - A list of any potential valuelists that may be needed, along with a brief description of each.
          - could be empty if there are no valuelists in the domain.                 
        """)

        self.insert_message_at_end(instructions)

    
    def insert_requirements_message(self, description: str) -> None:
        prompt = []
        prompt.append("The the description of the user's requirements is:")
        prompt.append(description)
        prompt.append(f"Turn this description into a complete requirements document.")
        self.insert_message_at_end("\n".join(prompt))


# ---------------------------------------------------------------------------------------------
# class ERDesignConversation:
# ---------------------------------------------------------------------------------------------
class ERDesignConversation(ERConversation):
    def __init__(self):
        super().__init__()

        instructions = dedent("""
        You are an expert ER model designer.
        You will be given a domain description.
        Design an ER model based on the domain description.
        Provide the output in YAML format according to the following schema:
        ```yaml
        # ----------------------------------------------------------
        # entities
        # ----------------------------------------------------------
        entities:
        # complete entity with key, keytype, and attributes
        - entityname: E1
          key: E1ID
          keytype: INTEGER
          attributes:
          - attributename: E1A1
            type: TEXT
          - attributename: E1A2
            type: DATE
            nullable: True
          - attributename: E1A3
            type: DECIMAL(9,2)

        # keytype not given, default to INTEGER
        - entityname: E2
          key: E2ID
          attributes:
          - attributename: E2A1
            type: TEXT

        # keytype not given, default to INTEGER
        - entityname: E3
          key: E3ID
          attributes:
          - attributename: E3A1
            type: DOUBLE
            nullable: True

        # key not given, inherited from superentity
        - entityname: E4
          attributes:
          - attributename: E4A1
            type: DOUBLE
            nullable: True

        # key not given, inherited from superentity
        - entityname: E5
          attributes:
          - attributename: E5A1
            type: TEXT

        # ----------------------------------------------------------
        # associative_entities
        # ----------------------------------------------------------
        associative_entities:
        # complete associative entity with local and global keys, attributes, and associations
        - associationname: AE1
          identification:
            localkey: AE1ID
            keytype: INTEGER
            global:
              - targetentity: E1
                role: RoleForGlobalKey
          associations:
          - targetentity: E2
            role: RoleForE2
            cardinality: ONE
          attributes:
          - attributename: AE1A1
            type: TEXT
          - attributename: AE1A2
            type: DECIMAL(9,2)
            nullable: True
          - attributename: AE1A3
            type: FLOAT

        # associative entity with without global key and without attributes
        - associationname: AE2
          identification:
            localkey: AE2ID
            keytype: INTEGER
          associations:
          - targetentity: E2
            role: RoleForE2
            cardinality: ONE

        # keytype not given for local key, default to INTEGER
        # role not given for global key, default to target entity name
        # role not given for association, default to target entity name
        # cardinality not given for association, default to ONE
        - associationname: AE3
          identification:
            localkey: AE3ID
            global:
              - targetentity: E1
          associations:
          - targetentity: AE1
          - targetentity: E2
            role: RoleForE2
            cardinality: MANY
          attributes:
          - attributename: AE3A1
            type: TEXT

        # identification not given, inherited from superentity
        - associationname: AE4
          associations:
          - targetentity: AE1
          attributes:
          - attributename: AE4A1
            type: TEXT

        # identification not given, inherited from superentity
        - associationname: AE5
          attributes:
          - attributename: AE5A1
            type: FLOAT

        # ----------------------------------------------------------
        # relationships
        # ----------------------------------------------------------
        relationships:
        # complete relationship with roles, cardinality, and attributes
        - relationshipname: R1
          entities:
          - targetentity: E1
            role: RoleForE1
            cardinality: ONE
          - targetentity: E2
            role: RoleForE2
            cardinality: MANY
          attributes:
          - attributename: R1A1
            type: DATE

        # role not given for entities, default to entity name
        - relationshipname: R2
          entities:
          - targetentity: E1
            cardinality: OPTIONAL_ONE
          - targetentity: E2
            cardinality: OPTIONAL_MANY
          attributes:
          - attributename: R2A1
            type: TEXT 
          - attributename: R2A2
            type: DECIMAL(9,2)
            nullable: True

        # ----------------------------------------------------------
        # inheritances
        # ----------------------------------------------------------
        inheritances:
        - superentity: E1
          subentities:
          - E4
          - E5
          # implementation not given, default to ONE_TABLE_PER_ENTITY
        - superentity: AE1
          subentities:
          - AE4
          - AE5
          implementation: ONE_TABLE
          # one table for all entities in the inheritance hierarchy, including the superentity and all subentities

        # ----------------------------------------------------------
        # valuelists
        # ----------------------------------------------------------
        valuelists:
        - valuelistname: VL1
          values:
          - Value1_1
          - Value1_2
          - Value1_3
          many_to_one_from_entities:
          - sourceentity: E1

        - valuelistname: VL2
          values:
          - Value2_1
          - Value2_2
          many_to_one_from_entities:
          - sourceentity: AE1
          - sourceentity: E2
        ```
        Adhere to the following design principles:
        - General principles
          - Don't provide entities and associative entities with the same name
          - Don't provide key for entity_sub, if entity_sub is subentity of entity_super
          - Don't provide identification for associative_entity_sub, if associative_entity_sub is subentity of associative_entity_sub

        - Entities
          - Should have only atomic keys, no composite keys 
          - Keyname should be entityname + "ID"
          - Keytype should be INTEGER

        - Associative Entities
          - Identification of associative entities
            - Only one local key - usually in case of junction entity with many associations to avoid complexity
            - Only one global key - usually in case of 1-ary associative entity, for one-to-one relationship
            - One local key + at most two global keys - e.g. Room entity with RoomID as local key and association to Building entity 
            - At most three global keys - usually in case of junction entity with many associations, but only three should be used to avoid complexity 
          - Associations to other entities
            - Each global key is an association to the target entity with a role
            - Additional associations can be added to the associative entity as needed, with appropriate cardinality via the yaml association element.
          - Roles and cardinalities in associations
            - Roles can have cardinality ONE, OPTIONAL_ONE, MANY, or OPTIONAL_MANY depending on the nature of the association and the business rules
            - Roles should express the meaning of the associative entity in relation to the target entity. 
            - If the only meaning is the association itself, then the role can be the same as the target entity name. 
            - Examples for meaning of the assocition itself
              - In a Room entity that is associated with a Building entity, the role of the association to Building can be "Building". 
              - In a Lineitem entity that is associated with Order and Product entities, the roles of the associations can be "Order" and "Product" respectively. 
              - In a University Course Enrollment entity that is associated with Student, Course, and Semester entities, the roles of the associations can be "Student", "Course", and "Semester" respectively. 
          - Don't repeat target entities: if it is in the identification element don't put it in the associations element again
          - Put targetentities that refer to valuelists into the many_to_one_from_entities element of that valuelist 

        - Relationships 
          - Roles and cardinalities in relationships: the same as in associative entities.
          - Don't repeat entities in the entities element that are already target entities in associative_entities.

        - Inheritances
          - "is-a" is of cardinality OPTIONAL_ONE on side of the superentity and ONE on the side of the subentity, , i.e. the subentity must be associated with exactly one superentity, while the superentity can be associated with zero or one subentity
          - All subentities within an inheritance must also be listed in the entities element or in the associative_entities element
          - All subentities should have at least one attribute specific to the subentity
          - Subentities of associative_entities must also be associative_entities

        - Valuelists
          - Dont't repeat valuelist names in entities 
          - Dont't repeat valuelist names as associative_entities 
                        
        Don't provide elements for associative_entities, relationships, inheritances, and valuelists if there are none in the domain.
        """)

        self.insert_message_at_end(instructions)

    
    def insert_design_message(self, description: str) -> None:
        prompt = []
        prompt.append("The following description is given:")
        prompt.append(description)
        prompt.append("Provide the design as valid yaml format as given before.")
        prompt.append("Only yaml format, without explanation.")
        self.insert_message_at_end("\n".join(prompt))

