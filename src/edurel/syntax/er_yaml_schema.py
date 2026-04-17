from strictyaml import Bool, Map, Optional, Regex, Seq, Str


ATTRIBUTE_TYPE = Regex(r"^[A-Za-z]+(?:\(\s*\d+\s*(?:,\s*\d+\s*)?\))?$")
CARDINALITY = Regex(r"^(?:ONE|MANY|OPTIONAL_ONE|OPTIONAL_MANY)$")
INHERITANCE_IMPLEMENTATION = Regex(r"^(?:ONE_TABLE_PER_ENTITY|ONE_TABLE)$")

attribute_schema = Map(
    {
        "attributename": Str(),
        "type": ATTRIBUTE_TYPE,
        Optional("nullable"): Bool(),
    }
)

entity_schema = Map(
    {
        "entityname": Str(),
        Optional("key"): Str(),
        Optional("keytype"): ATTRIBUTE_TYPE,
        Optional("attributes"): Seq(attribute_schema),
    }
)

global_key_schema = Map(
    {
        "targetentity": Str(),
        Optional("role"): Str(),
    }
)

identification_schema = Map(
    {
        Optional("localkey"): Str(),
        Optional("keytype"): ATTRIBUTE_TYPE,
        Optional("global"): Seq(global_key_schema),
    }
)

association_schema = Map(
    {
        "targetentity": Str(),
        Optional("role"): Str(),
        Optional("cardinality"): CARDINALITY,
    }
)

associative_entity_schema = Map(
    {
        "associationname": Str(),
        Optional("identification"): identification_schema,
        Optional("associations"): Seq(association_schema),
        Optional("attributes"): Seq(attribute_schema),
    }
)

relationship_participant_schema = Map(
    {
        "targetentity": Str(),
        Optional("role"): Str(),
        Optional("cardinality"): CARDINALITY,
    }
)

relationship_schema = Map(
    {
        "relationshipname": Str(),
        "entities": Seq(relationship_participant_schema),
        Optional("attributes"): Seq(attribute_schema),
    }
)

inheritance_schema = Map(
    {
        "superentity": Str(),
        "subentities": Seq(Str()),
        Optional("implementation"): INHERITANCE_IMPLEMENTATION,
    }
)

many_to_one_entity_schema = Map(
    {
        "sourceentity": Str(),
    }
)

valuelist_schema = Map(
    {
        "valuelistname": Str(),
        "values": Seq(Str()),
        Optional("many_to_one_from_entities"): Seq(many_to_one_entity_schema),
    }
)

schema = Map(
    {
        Optional("entities"): Seq(entity_schema),
        Optional("associative_entities"): Seq(associative_entity_schema),
        Optional("relationships"): Seq(relationship_schema),
        Optional("inheritances"): Seq(inheritance_schema),
        Optional("valuelists"): Seq(valuelist_schema),
    }
)
