from strictyaml import Bool, Map, Optional, Regex, Seq, Str


SQL_TYPE = Regex(r"^[A-Za-z]+(?:\(\s*\d+\s*(?:,\s*\d+\s*)?\))?$")

column_schema = Map(
    {
        "columnname": Str(),
        "type": SQL_TYPE,
        Optional("nullable"): Bool(),
    }
)

foreign_key_schema = Map(
    {
        Optional("fkname"): Str(),
        "sourcecolumns": Seq(Str()),
        "targettable": Str(),
        "targetcolumns": Seq(Str()),
    }
)

table_schema = Map(
    {
        "tablename": Str(),
        "columns": Seq(column_schema),
        Optional("primary_key"): Seq(Str()),
        Optional("foreign_keys"): Seq(foreign_key_schema),
    }
)

datalist_schema = Map(
    {
        "tablename": Str(),
        "values": Seq(Str()),
    }
)

schema = Map(
    {
        "tables": Seq(table_schema),
        Optional("datalists"): Seq(datalist_schema),
    }
)
