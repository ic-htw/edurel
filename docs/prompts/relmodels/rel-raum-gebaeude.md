### erstelle ein relationales modell as yaml-stuktur
- es soll die entitäten person, bestellung und produkte umfassen
- definiere passende beziehungen

### erstelle ein relationales datenmmodell
- es soll räume und gebäude umfassen
- definiere passende beziehungen
- die ausgabe des modells soll als yaml-stuktur erfolgen
- die ausgabe soll folgendes format haben
```yaml
tables:
- name: table1
  columns:
  - name: id1
    type: INTEGER
    nullable: False
  - name: attribute1
    type: TEXT
    nullable: True
  primary_key:
  - id1
- name: table2
  columns:
  - name: id2
    type: INTEGER
    nullable: False
  - name: fk1
    type: INTEGER
    nullable: False
  - name: attribute2
    type: DATE
    nullable: False
  - name: attribute3
    type: DECIMAL
    nullable: False
  primary_key:
  - id2
  foreign_keys:
  - name: fk_table2_table1
    - fk1
    ref_table: table1
    ref_columns:
    - id1
```
