CREATE TABLE raumart (
    raid INTEGER NOT NULL,
    bez  VARCHAR NOT NULL,
    CONSTRAINT raumart_pk PRIMARY KEY (raid)
);

CREATE TABLE ausstattungsart (
    aaid INTEGER NOT NULL,
    bez  VARCHAR NOT NULL,
    CONSTRAINT ausstattungsart_pk PRIMARY KEY (aaid)
);

CREATE TABLE gebaeude (
    gid      INTEGER NOT NULL,
    bez      VARCHAR NOT NULL,
    standort VARCHAR NOT NULL,
    CONSTRAINT gebaeude_pk PRIMARY KEY (gid)
);

CREATE TABLE raum (
    rid         INTEGER NOT NULL,
    raumnr      VARCHAR NOT NULL,
    anzahlsitze INTEGER NOT NULL,
    gid         INTEGER NOT NULL,
    raid        INTEGER NOT NULL,
    CONSTRAINT raum_pk PRIMARY KEY (rid),
    CONSTRAINT raum_gebaeude_fk FOREIGN KEY (gid) 
      REFERENCES gebaeude (gid),
    CONSTRAINT raum_raumart_fk FOREIGN KEY (raid)
      REFERENCES raumart (raid)
);

CREATE TABLE ausstattung (
    rid    INTEGER NOT NULL,
    aaid   INTEGER NOT NULL,
    anzahl INTEGER NOT NULL,
    CONSTRAINT ausstattung_pk PRIMARY KEY (rid, aaid),
    CONSTRAINT ausstattung_ausstattungsart_fk FOREIGN KEY (aaid)
      REFERENCES ausstattungsart (aaid),
    CONSTRAINT ausstattung_raum_fk FOREIGN KEY (rid)
      REFERENCES raum (rid)
);

CREATE TABLE staging (
    raumnr      VARCHAR,
    anzahlsitze      VARCHAR,
    ausstattung      VARCHAR,
    raumart      VARCHAR,
    gebaeude      VARCHAR,
    standort      VARCHAR
);
