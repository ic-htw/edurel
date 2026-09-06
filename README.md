# edurel — Education Tools for Relational Data

`edurel` is a teaching library for database courses. You describe a data model **once**, in YAML,
and the library translates it into every representation a course needs: an ER class diagram, a
logical relational schema, SQL DDL, Mermaid diagrams, and ready-to-run DuckDB databases. It also
ships LangChain conversation classes that let students generate and critique ER models, SQL queries,
and test data with an LLM.

It is designed to be used from Jupyter notebooks: every representation is available as a string
(`get_*`), as rendered notebook output (`display_*`), and as a file (`save_*`).

```
                                  ┌──────────────────┐
                                  │  ER YAML         │  conceptual model
                                  └────────┬─────────┘
                                           │ ERSchemaMan
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
      ER class diagram              ER YAML (normalized)          RelSchema (AST)
        (Mermaid)                                                       │
                                                                        │ RelSchemaMan
                                       ┌────────────────┬───────────────┼────────────────┐
                                       │                │               │                │
                                  Rel YAML         ER diagram       SQL DDL          structure
                                                   (Mermaid)     (+ INSERTs)          listing
                                                                        │
                                                                        │ DuckDbMan
                                                                   live database
                                                                  (and back to YAML)
```

* **Conceptual layer (ER):** entities, associative entities, relationships, inheritances, valuelists.
* **Logical layer (Rel):** tables, columns, primary keys, foreign keys, datalists.

Both layers have the same shape — YAML schema → AST → validation → visitor/builder translation →
notebook facade — so what students learn on one side transfers directly to the other.

---

## Installation

```bash
pip install edurel
```

Requires Python ≥ 3.12.

Rendering Mermaid diagrams to PNG (`save_mermaid_diagram()`) shells out to the Mermaid CLI:

```bash
npm install -g @mermaid-js/mermaid-cli
```

`display_*` methods need IPython (they are meant for notebooks); `jupyter` brings it in.

---

## Quick start

`er.yaml` — a tiny course-registration model:

```yaml
entities:
- entityname: Student
  key: StudentID
  keytype: INTEGER
  attributes:
  - attributename: Name
    type: VARCHAR(100)
  - attributename: Email
    type: VARCHAR(200)
    nullable: TRUE

- entityname: Course
  key: CourseID
  keytype: INTEGER
  attributes:
  - attributename: Title
    type: VARCHAR(200)
  - attributename: Credits
    type: INTEGER

associative_entities:
- associationname: Enrollment
  identification:
    global:
    - targetentity: Student
    - targetentity: Course
  attributes:
  - attributename: EnrolledOn
    type: DATE

valuelists:
- valuelistname: EnrollmentStatus
  values:
  - Applied
  - Admitted
  - Rejected
  many_to_one_from_entities:
  - sourceentity: Enrollment
```

```python
from edurel.core.er_schema_man import ERSchemaMan
from edurel.core.rel_schema_man import RelSchemaMan

er = ERSchemaMan.fromFile("er.yaml")     # parse + validate the conceptual model
rel = RelSchemaMan.fromAST(er.get_rel()) # derive the logical model

er.display_mermaid_diagram(direction="LR")  # ER class diagram in the notebook
rel.display_mermaid_diagram(direction="LR") # ER diagram of the derived tables
rel.display_sql()                           # CREATE TABLE + ALTER TABLE + INSERT
```

---

## Sample code usage

Every snippet below is self-contained and was run against the model in
[Quick start](#quick-start). Outputs are the real, unedited outputs.

### 1. From ER YAML to an ER class diagram

```python
from edurel.core.er_schema_man import ERSchemaMan

er = ERSchemaMan.fromFile("er.yaml")
print(er.get_mermaid_code(direction="LR"))
```

```
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
    EnrollmentStatus: Applied, Admitted, Rejected
    "
    class Student:::entityStyle {
        +Name VARCHAR[100]
        -Email VARCHAR[200]
        **key**(StudentID INTEGER)
    }
    class Course:::entityStyle {
        +Title VARCHAR[200]
        +Credits INTEGER
        **key**(CourseID INTEGER)
    }
    class Enrollment {
        +EnrolledOn DATE
        **global_key**(Student)
        **global_key**(Course)
        **vl**(EnrollmentStatus)
    }
    Enrollment "1..*" -- "0..1" Student : Student
    Enrollment "1..*" -- "0..1" Course : Course

    classDef entityStyle fill:#d0d0d0,stroke:#333,stroke-width:2px
```

Reading the class bodies: `+` is a mandatory attribute, `-` a nullable one, `**key**` /
`**local_key**` / `**global_key**` mark identification, and `**vl**(...)` marks a valuelist that
the class references. Entities get the grey `entityStyle`; associative entities are blue.

Other ways to construct the manager:

```python
ERSchemaMan.fromStr(yaml_text)                  # from a YAML string
ERSchemaMan.fromFile("er.yaml")                 # from a file
ERSchemaMan.fromURL("https://.../er.yaml")      # from a URL
ERSchemaMan.fromAST(er_schema)                  # from an er_ast.ERSchema you built yourself
```

### 2. ER model → relational schema → SQL

`ERSchemaMan.get_rel()` returns a **`rel_ast.RelSchema`** (not a string); hand it to
`RelSchemaMan.fromAST()` to continue on the logical layer.

```python
from edurel.core.rel_schema_man import RelSchemaMan

rel = RelSchemaMan.fromAST(er.get_rel())
print(rel.get_structure())   # compact overview: tables and foreign keys
```

```
- table: Student(StudentID, Name, Email)
- table: Course(CourseID, Title, Credits)
- table: EnrollmentStatus(ID, Description, IsValid, SortOrder)
- table: Enrollment(StudentID, CourseID, EnrolledOn, EnrollmentStatusID)
- fk: Enrollment(StudentID)->Student(StudentID)
- fk: Enrollment(CourseID)->Course(CourseID)
- fk: Enrollment(EnrollmentStatusID)->EnrollmentStatus(ID)
```

```python
print(rel.get_sql())
```

```sql
CREATE TABLE Student (
  StudentID INTEGER NOT NULL,
  Name VARCHAR(100) NOT NULL,
  Email VARCHAR(200),
  PRIMARY KEY (StudentID)
);
CREATE TABLE Course (
  CourseID INTEGER NOT NULL,
  Title VARCHAR(200) NOT NULL,
  Credits INTEGER NOT NULL,
  PRIMARY KEY (CourseID)
);
CREATE TABLE EnrollmentStatus (
  ID INTEGER NOT NULL,
  Description VARCHAR(100) NOT NULL,
  IsValid INTEGER NOT NULL,
  SortOrder INTEGER NOT NULL,
  PRIMARY KEY (ID)
);
CREATE TABLE Enrollment (
  StudentID INTEGER NOT NULL,
  CourseID INTEGER NOT NULL,
  EnrolledOn DATE NOT NULL,
  EnrollmentStatusID INTEGER NOT NULL,
  PRIMARY KEY (StudentID, CourseID)
);
ALTER TABLE Enrollment
  ADD CONSTRAINT fk_Enrollment_Student FOREIGN KEY (StudentID) REFERENCES Student (StudentID);
ALTER TABLE Enrollment
  ADD CONSTRAINT fk_Enrollment_Course FOREIGN KEY (CourseID) REFERENCES Course (CourseID);
ALTER TABLE Enrollment
  ADD CONSTRAINT fk_Enrollment_EnrollmentStatus FOREIGN KEY (EnrollmentStatusID) REFERENCES EnrollmentStatus (ID);
INSERT INTO EnrollmentStatus (ID, Description, IsValid, SortOrder) VALUES (1, 'Applied', 1, 1);
INSERT INTO EnrollmentStatus (ID, Description, IsValid, SortOrder) VALUES (2, 'Admitted', 1, 2);
INSERT INTO EnrollmentStatus (ID, Description, IsValid, SortOrder) VALUES (3, 'Rejected', 1, 3);
```

Two FK styles are available:

| call | foreign keys | table order |
| --- | --- | --- |
| `rel.get_sql()` (`fk_external=True`, default) | trailing `ALTER TABLE ... ADD CONSTRAINT` | declaration order |
| `rel.get_sql(fk_external=False)` | inline `FOREIGN KEY` inside `CREATE TABLE` | topological (FK targets first); constraints that would close a cycle are emitted as comments |

`fk_external=False` internally calls `rel_ast.enrich_ast()`, which fills in `Table.level` and
`ForeignKey.is_cycle`.

### 3. Load the schema into DuckDB and query it

DuckDB does not support `ALTER TABLE ... ADD CONSTRAINT FOREIGN KEY`, so use the inline-FK variant
when feeding it a schema.

```python
from edurel.core.duckdb_man import DuckDbMan

db = DuckDbMan.fromMem("courses")
db.execute(rel.get_sql(fk_external=False))

print(db.get_tablenames())
print(db.sql("SELECT * FROM EnrollmentStatus ORDER BY SortOrder"))
```

```
['Course', 'Enrollment', 'EnrollmentStatus', 'Student']
┌───────┬─────────────┬─────────┬───────────┐
│  ID   │ Description │ IsValid │ SortOrder │
│ int32 │   varchar   │  int32  │   int32   │
├───────┼─────────────┼─────────┼───────────┤
│     1 │ Applied     │       1 │         1 │
│     2 │ Admitted    │       1 │         2 │
│     3 │ Rejected    │       1 │         3 │
└───────┴─────────────┴─────────┴───────────┘
```

More `DuckDbMan` entry points and helpers:

```python
DuckDbMan.fromMem("scratch")                          # in-memory
DuckDbMan.fromFile("data/library.duckdb")             # file, read-only by default
DuckDbMan.fromURL("library.duckdb",                   # download once, then open
                  base_url="https://example.org/db",
                  save_dir="data")

db.sql_df("SELECT Description FROM EnrollmentStatus") # pandas DataFrame
db.sql_nx("SELECT * FROM Nope")                       # never raises: "err: Catalog Error: ..."
db.sql_file("queries/q1.sql")                         # run SQL from a file
db.export_data_as_insert_statements(["EnrollmentStatus"])
db.close()
```

`sql_nx` returning an error string instead of raising is deliberate: a student's broken query
should not stop the notebook.

```
err: Catalog Error: Table with name Nope does not exist!
Did you mean "Course"?
```

### 4. Round-trip an existing database back into the model

`DuckDbMan.get_yaml()` introspects a live database and emits YAML in the *rel* schema shape, so any
existing database can re-enter the pipeline.

```python
rel_from_db = RelSchemaMan.fromStr(db.get_yaml())
print(rel_from_db.get_structure())
```

```
- table: Course(CourseID, Title, Credits)
- table: Enrollment(StudentID, CourseID, EnrolledOn, EnrollmentStatusID)
- fk: Enrollment(StudentID)->Student(StudentID)
- fk: Enrollment(CourseID)->Course(CourseID)
- fk: Enrollment(EnrollmentStatusID)->EnrollmentStatus(ID)
- table: EnrollmentStatus(ID, Description, IsValid, SortOrder)
- table: Student(StudentID, Name, Email)
```

From there you can diagram it (`rel_from_db.display_mermaid_diagram()`) or re-emit portable SQL.

### 5. Relational Mermaid diagram

```python
print(rel.get_mermaid_code(direction="LR"))
```

(abridged — the `Course` and `EnrollmentStatus` blocks are omitted at the `...`)

```
erDiagram
  direction LR
  Student {
    INTEGER StudentID PK"NOT NULL"
    VARCHAR(100) Name"NOT NULL"
    VARCHAR(200) Email"NULL"
  }
  ...
  Enrollment {
    INTEGER StudentID PK, FK"NOT NULL"
    INTEGER CourseID PK, FK"NOT NULL"
    DATE EnrolledOn"NOT NULL"
    INTEGER EnrollmentStatusID FK"NOT NULL"
  }
  Enrollment }|--o| Student : "StudentID -> StudentID"
  Enrollment }|--o| Course : "CourseID -> CourseID"
  Enrollment }|--o| EnrollmentStatus : "EnrollmentStatusID -> ID"
```

The connector encodes optionality: `}|--o|` for a mandatory FK, `}o--o|` when any FK column is
nullable. Column types keep their size but are squeezed into a single token
(`DECIMAL(9, 2)` → `DECIMAL(9_2)`), because Mermaid rejects whitespace inside an attribute type.

### 6. Build a schema in Python instead of YAML

The AST dataclasses are public, so a notebook can construct or transform a model directly.

```python
from edurel.syntax.rel_ast import Column, ForeignKey, RelSchema, Table
from edurel.core.rel_schema_man import RelSchemaMan

rel_schema = RelSchema(
    tables=[
        Table(
            tablename="Student",
            columns=[
                Column(columnname="StudentID", type="INTEGER"),
                Column(columnname="Email", type="VARCHAR(200)", nullable=True),
            ],
            primary_key=["StudentID"],
        ),
        Table(
            tablename="Enrollment",
            columns=[
                Column(columnname="EnrollmentID", type="INTEGER"),
                Column(columnname="StudentID", type="INTEGER"),
            ],
            primary_key=["EnrollmentID"],
            foreign_keys=[
                ForeignKey(
                    fkname="fk_Enrollment_Student",
                    sourcecolumns=["StudentID"],
                    targettable="Student",
                    targetcolumns=["StudentID"],
                )
            ],
        ),
    ]
)

man = RelSchemaMan.fromAST(rel_schema)
print(man.get_sql())
print(man.get_yaml())      # and back to YAML
```

`fromAST` deep-copies its argument, so the manager cannot be mutated from the outside by accident.
The ER side works the same way with `edurel.syntax.er_ast` (`ERSchema`, `Entity`, `Attribute`,
`AssociativeEntity`, `Identification`, `GlobalKey`, `Association`, `Relationship`,
`RelationshipEntity`, `Inheritance`, `ValueList`, `ManyToOneEntity`).

### 7. Error messages built for students

YAML parsing raises `ValueError` in a fixed, readable shape — `Location`, `Problem`, `Context`,
`Snippet`, `Potential fix` — and never lets the underlying strictyaml/sqlglot exception through.

```python
ERSchemaMan.fromStr("""
entities:
- entityname: Student
  keytype: NOT A TYPE
""".strip())
```

```
ValueError: YAML validation failed.
Location: line 3, column 1.
Problem: found non-matching string.
Context: when expecting string matching ^[A-Za-z]+(?:\(\s*\d+\s*(?:,\s*\d+\s*)?\))?$.
Snippet: keytype: NOT A TYPE
    ^ (line: 3)
Potential fix: Check the field format against the schema. SQL types should look like `INTEGER`, `TEXT`, `VARCHAR(255)`, or `DECIMAL(9, 2)`.
```

Semantic validation collects **all** problems and reports them as one bulleted list:

```python
ERSchemaMan.fromStr("""
entities:
- entityname: Student
  key: StudentID
- entityname: Student
  key: SID
relationships:
- relationshipname: Attends
  entities:
  - targetentity: Student
    cardinality: ONE
  - targetentity: Ghost
    cardinality: MANY
""".strip())
```

```
ValueError: AST validation failed:
- Duplicate entityname 'Student'.
- Relationship 'Attends' targetentity 'Ghost' does not exist as entityname or associationname.
```

### 8. SQL helpers

`edurel.utils.sql` validates and transpiles SQL with sqlglot, using PostgreSQL as the source
dialect, and reports failures in the same student-friendly shape.

```python
from edurel.utils.sql import sql_extract, transpile_postgres_sql, validate_postgres_sql

sql = "SELECT s.Name FROM Student s JOIN Enrollment e ON e.StudentID = s.StudentID LIMIT 5"

validate_postgres_sql(sql)                       # raises ValueError if invalid
print(transpile_postgres_sql(sql, "duckdb"))
# SELECT s.Name FROM Student AS s JOIN Enrollment AS e ON e.StudentID = s.StudentID LIMIT 5

print(sql_extract("here you go:\n```sql\nSELECT 1;\n```"))   # pull SQL out of an LLM answer
# SELECT 1;
```

```python
validate_postgres_sql("SELECT FROM WHERE")
```

```
ValueError: SQL validation failed.
Location: line 1, column 17.
Problem: Expected table name but got <Token token_type: TokenType.WHERE, ...>.
Context: PostgreSQL parsing failed..
Snippet: SELECT FROM WHERE
Potential fix: Add the missing table name after the clause that references a table.
```

`edurel.utils.md` has the markdown-side counterparts: `md_sql`, `md_yaml`, `md_plain`,
`display_md`, `display_sql`, `display_yaml`, plus `sql_extract` / `yaml_extract` for pulling fenced
code blocks out of LLM replies. (`sql_extract` exists identically in both modules; the one in
`utils.sql` is the one the validation/transpile path uses.)

### 9. LLM conversations

The `llm` package wraps LangChain chat models in a small, *editable* message list. The subclasses
carry no logic — they preload the course's system prompts and instructions.

| class | module | purpose |
| --- | --- | --- |
| `Conversation` | `llm.conversation_base` | base message list: set/insert/replace/delete/slice/display |
| `ERConversation` | `llm.conversation_er` | shared ER modelling vocabulary |
| `ERRequirementsConversation` | `llm.conversation_er` | domain description → structured requirements document |
| `ERDesignConversation` | `llm.conversation_er` | domain description → ER YAML in this library's schema |
| `SQLGenConversation` | `llm.conversation_rel` | natural-language question → SQL for a given schema |
| `DataGenConversation` | `llm.conversation_rel` | schema (+ existing rows) → synthetic `INSERT` statements |

Designing an ER model and feeding the answer straight back into the pipeline:

```python
from langchain_openai import ChatOpenAI          # needs OPENAI_API_KEY in the environment
from edurel.llm.conversation_er import ERDesignConversation
from edurel.core.er_schema_man import ERSchemaMan
from edurel.utils.md import yaml_extract

model = ChatOpenAI(model="<your-model>")

conv = ERDesignConversation()
conv.insert_design_message("A small library that lends books to members.")
answer = conv.call_llm(model)

er = ERSchemaMan.fromStr(yaml_extract(answer))   # validated immediately — errors are teachable
er.display_mermaid_diagram()
```

Generating test data for a schema you just derived:

```python
from edurel.llm.conversation_rel import DataGenConversation
from edurel.utils.md import sql_extract

conv = DataGenConversation()
conv.set_database_schema(rel.get_yaml())
conv.insert_datagen_message(no_of_records_per_table=10, exclude_tables=["EnrollmentStatus"])

db.execute(sql_extract(conv.call_llm(model)))
```

Asking questions about a database:

```python
from edurel.llm.conversation_rel import SQLGenConversation

conv = SQLGenConversation()
conv.set_database_schema(db.get_yaml())
conv.insert_question_message("How many students are enrolled in each course?")
print(db.sql_nx(sql_extract(conv.call_llm(model))))
```

Because the history is a plain list, notebooks can rewrite it — useful for showing how prompt
context changes an answer:

```python
conv.display()                          # numbered transcript, rendered as Markdown
conv.display(lastn_only=2)
conv.len()
conv.get_messages_by_gslice("0, 2:5, -1")   # generalized slicing, see utils.misc.gslice
conv.replace_message_at_index(2, "Ask more precisely: ...")
conv.delete_messages_by_slice(3, None)
conv.clear_messages(keep_system=True)
conv.gen_prompt("0:2")                  # the raw text that would be sent
```

`call_llm` never raises: a failed call comes back as the string `"err: ..."`, mirroring
`DuckDbMan.sql_nx`.

### 10. Saving artefacts from a notebook

Every representation has a `save_*` counterpart. Saving is a **no-op unless `overwrite=True`**, so
re-running a notebook cell cannot silently destroy a student's edited file. The target directory
must already exist — it is not created for you.

```python
from pathlib import Path
Path("out").mkdir(exist_ok=True)

er.save_yaml("out/er.yaml")
er.save_mermaid_code("out/er.mmd", direction="LR")
er.save_mermaid_diagram("out/er.png", direction="LR", scale=2.0)   # needs mmdc

rel.save_yaml("out/rel.yaml", overwrite=True)
rel.save_sql("out/schema.sql", fk_external=False, overwrite=True)
rel.save_mermaid_diagram("out/rel.png", width=1600, height=900, overwrite=True)
```

Each call prints what it did:

```
Text saved to out/er.yaml
File out/er.yaml already exists. Use overwrite=True to overwrite.
```

### 11. Adding your own output format

Output formats are **builders**. Subclass the builder ABC, implement every hook (return `None` for
the ones you do not need), and let the visitor walk the AST — builders never traverse it themselves.

```python
from edurel.translation.rel_trans import (
    RelSchemaTranslationBuilder,
    RelSchemaTranslationVisitor,
)

class MarkdownTranslationBuilder(RelSchemaTranslationBuilder):
    def __init__(self) -> None:
        self.lines: list[str] = []

    def start_schema(self, rel_schema): self.lines = []
    def end_schema(self, rel_schema): return None

    def start_table(self, table):
        self.lines += [f"### {table.tablename}", "",
                       "| column | type | null |", "| --- | --- | --- |"]

    def add_column(self, table, column):
        null = "yes" if column.nullable else "no"
        self.lines.append(f"| {column.columnname} | {column.type} | {null} |")

    def add_primary_key(self, table): return None
    def add_foreign_key(self, table, foreign_key): return None
    def end_table(self, table): self.lines.append("")
    def add_datalist(self, datalist): return None

    def build(self): return "\n".join(self.lines)

builder = MarkdownTranslationBuilder()
RelSchemaTranslationVisitor(builder).visit(rel.get_ast())
print(builder.build())
```

```
### Student

| column | type | null |
| --- | --- | --- |
| StudentID | INTEGER | no |
| Name | VARCHAR(100) | no |
| Email | VARCHAR(200) | yes |
...
```

To make it a first-class notebook citizen, add the `get_X` / `display_X` / `save_X` triplet to
`RelSchemaMan` (see `get_structure` for the smallest possible example).

---

## YAML reference

### ER YAML

All five top-level sections are optional. The listing below is a key reference — it shows every
supported key, not a semantically complete model. Parsing uses
[strictyaml](https://hitchdev.com/strictyaml/), so **block style only** — `[a, b]` and `{k: v}` are
rejected with an explicit error.

```yaml
entities:                        # independently identified things
- entityname: Course
  key: CourseID                  # optional
  keytype: INTEGER               # optional, INTEGER by default
  attributes:
  - attributename: Title
    type: VARCHAR(200)
    nullable: TRUE               # optional, FALSE by default

associative_entities:            # things identified through other things
- associationname: Enrollment
  identification:
    localkey: EnrollmentID       # own surrogate key, and/or ...
    keytype: INTEGER
    global:                      # ... identification borrowed from other entities
    - targetentity: Student
      role: student              # optional, renames the derived FK column/constraint
  associations:                  # n-ary links to other (associative) entities
  - targetentity: Course
    role: course
    cardinality: ONE             # ONE | MANY | OPTIONAL_ONE | OPTIONAL_MANY
  attributes:
  - attributename: EnrolledOn
    type: DATE

relationships:                   # binary relationships between exactly two participants
- relationshipname: Wrote
  entities:
  - targetentity: Person
    role: author
    cardinality: MANY
  - targetentity: Book
    cardinality: MANY
  attributes:
  - attributename: Contribution
    type: VARCHAR(50)

inheritances:                    # subentities are associative entities
- superentity: Person
  subentities:
  - Student
  - Employee
  implementation: ONE_TABLE_PER_ENTITY   # ONE_TABLE parses but is not implemented

valuelists:                      # small controlled vocabularies
- valuelistname: EnrollmentStatus
  values:
  - Applied
  - Admitted
  - Rejected
  many_to_one_from_entities:
  - sourceentity: Enrollment
```

Types must match `^[A-Za-z]+(?:\(\s*\d+\s*(?:,\s*\d+\s*)?\))?$` — that is, a bare type name with
an optional size or precision/scale: `INTEGER`, `TEXT`, `VARCHAR(255)`, `DECIMAL(9, 2)`.

A few YAML keys are renamed on the way into the AST:

| YAML key | AST field |
| --- | --- |
| `identification.global` | `Identification.global_keys` |
| relationship `entities[].targetentity` | `RelationshipEntity.entityname` |
| valuelist `many_to_one_from_entities[].sourceentity` | `ManyToOneEntity.entityname` |

### Rel YAML

```yaml
tables:
- tablename: Enrollment
  columns:
  - columnname: EnrollmentID
    type: INTEGER
  - columnname: StudentID
    type: INTEGER
    nullable: FALSE              # optional, FALSE by default
  primary_key:
  - EnrollmentID
  foreign_keys:
  - fkname: fk_Enrollment_Student
    sourcecolumns:
    - StudentID
    targettable: Student
    targetcolumns:
    - StudentID

datalists:                       # seed rows for a valuelist-style table
- tablename: EnrollmentStatus
  values:
  - Applied
  - Admitted
  - Rejected
```

A `datalist` renders as
`INSERT INTO <name> (ID, Description, IsValid, SortOrder) VALUES (<n>, '<value>', 1, <n>);`.

---

## Translation rules

These conventions are baked into the ER → Rel translation and pinned by the test suite.

**Relationships.** With `A` and `B` the two participants:

| cardinalities | result |
| --- | --- |
| many ↔ many | bridge table named after the relationship, PK = both FKs |
| many ↔ one | FK column on the *many* side |
| one ↔ one | direct FK; when exactly one side is optional the FK lands on the mandatory side |

In a mandatory 1:1 the FK reuses the PK column of the table that carries it; otherwise it is a
separate column. An FK column becomes nullable when the side carrying it is `OPTIONAL_*`. A `role`
renames the FK column (`author` → `authorID`) and the constraint (`fk_Wrote_author`).

**Associative entities.** A `localkey` becomes the table's own PK column; each `global` entry
contributes the target's PK column(s) to both the PK and an FK. Plain `associations` become FKs.

**Inheritance.** Each subentity table receives the superentity's PK columns as its own PK *and* as
an FK named `fk_<sub>_<super>`. Subentities are modelled as associative entities without their own
identification. `implementation: ONE_TABLE` is accepted by the YAML schema but not honoured by the
translation.

**Valuelists.** A valuelist becomes a table with exactly `ID / Description / IsValid / SortOrder`
plus a `DataList`; every referencing entity gets a `<Valuelist>ID` FK column.

**Defaults.** A missing `keytype` or attribute `type` is `INTEGER`; a missing `cardinality` is
`ONE`.

---

## API overview

### `ERSchemaMan` (`edurel.core.er_schema_man`)

Constructors: `fromStr`, `fromFile`, `fromURL`, `fromAST`.

| representation | methods |
| --- | --- |
| AST | `get_ast`, `display_ast` |
| ER YAML | `get_yaml`, `display_yaml`, `save_yaml` |
| relational AST | `get_rel`, `display_rel`, `save_rel` |
| Mermaid class diagram | `get_mermaid_code`, `display_mermaid_code`, `save_mermaid_code`, `display_mermaid_diagram`, `save_mermaid_diagram` |

> `get_rel()` returns a `rel_ast.RelSchema` object despite its `-> str` annotation; the intended
> next step is `RelSchemaMan.fromAST(er.get_rel())`.

### `RelSchemaMan` (`edurel.core.rel_schema_man`)

Constructors: `fromStr`, `fromFile`, `fromURL`, `fromAST`.

| representation | methods |
| --- | --- |
| AST | `get_ast`, `display_ast` |
| Rel YAML | `get_yaml`, `display_yaml`, `save_yaml` |
| SQL DDL | `get_sql`, `display_sql`, `save_sql` (all take `fk_external`) |
| Mermaid ER diagram | `get_mermaid_code`, `display_mermaid_code`, `save_mermaid_code`, `display_mermaid_diagram`, `save_mermaid_diagram` |
| structure listing | `get_structure`, `display_structure` |

### `DuckDbMan` (`edurel.core.duckdb_man`)

Constructors: `fromMem`, `fromFile`, `fromURL`.

Execution: `execute`, `execute_file`, `sql`, `sql_nx`, `sql_file`, `sql_df`, `sql_file_df`,
`print`, `close`.
Introspection: `get_tablenames`, `get_columns`, `get_primary_keys`, `get_foreign_keys`, `get_yaml`,
`export_data_as_insert_statements`.

---

## Project layout

```
src/edurel/
  syntax/        er_yaml_schema.py, rel_yaml_schema.py   strictyaml schemas
                 er_ast.py, rel_ast.py                   dataclasses, *AstFactory, validate_ast,
                                                         enrich_ast (levels + FK cycles)
  translation/   er_trans.py, rel_trans.py               visitors + builders (YAML, Mermaid, SQL,
                                                         structure, ER→Rel)
  core/          er_schema_man.py, rel_schema_man.py     notebook facades
                 duckdb_man.py                           DuckDB wrapper + introspection
  llm/           conversation_base.py                    editable LangChain message list
                 conversation_er.py, conversation_rel.py course prompts
  utils/         yaml.py, sql.py, md.py, mermaid.py, misc.py
```

The ER and Rel stacks are deliberately parallel, and several class names (`YamlTranslationBuilder`,
`MermaidTranslationBuilder`) exist in both — always import them qualified by module.
`src/edurel/` uses implicit namespace packages (no `__init__.py`).

---

## Development

```bash
uv run --extra dev --extra notebook pytest -q      # test suite
uv run --extra dev black src tests                 # line-length 88
uv run --extra dev ruff check src tests
uv build                                           # wheel + sdist into dist/
```

`--extra notebook` is needed even for tests: IPython is imported at module scope by `utils/md.py`,
`utils/mermaid.py`, and `llm/conversation_base.py`, and only arrives with `jupyter`. In an activated
virtualenv that already has the dev and notebook dependencies, drop the `uv run --extra ...` prefix
and call `pytest` / `black` / `ruff` directly.

Adding an AST node type touches, in order: the strictyaml schema, the dataclass, the
`*AstFactory.create_*`, `validate_ast`, the builder ABC, **every** builder subclass, and the
visitor. The tests use a `RecordingBuilder` that asserts on the hook-call sequence, so
traversal-order changes surface there.

---

## License

MIT — see [LICENSE](LICENSE).
