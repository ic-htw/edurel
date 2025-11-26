-- Tables with no dependencies
CREATE TABLE modulart (
    maid  INTEGER NOT NULL,
    bez   TEXT NOT NULL,
    aktiv TEXT NOT NULL,
    lfdnr INTEGER NOT NULL,
    CONSTRAINT modulart_pk PRIMARY KEY ( maid )
);

CREATE TABLE modulbtart (
    mbaid INTEGER NOT NULL,
    bez   TEXT NOT NULL,
    aktiv TEXT NOT NULL,
    lfdnr INTEGER NOT NULL,
    CONSTRAINT modulbtart_pk PRIMARY KEY ( mbaid )
);

CREATE TABLE person (
    pid  INTEGER NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT person_pk PRIMARY KEY ( pid )
);

CREATE TABLE raum (
    rid    INTEGER NOT NULL,
    raumnr TEXT NOT NULL,
    CONSTRAINT raum_pk PRIMARY KEY ( rid )
);

CREATE TABLE rolle (
    rid INTEGER NOT NULL,
    bez TEXT NOT NULL,
    CONSTRAINT rolle_pk PRIMARY KEY ( rid )
);

CREATE TABLE semester (
    sid      INTEGER NOT NULL,
    bez      TEXT NOT NULL,
    beginn   DATE NOT NULL,
    ende     DATE NOT NULL,
    vlbeginn DATE NOT NULL,
    vlende   DATE NOT NULL,
    CONSTRAINT semester_pk PRIMARY KEY ( sid )
);

CREATE TABLE tag (
    tid INTEGER NOT NULL,
    bez TEXT NOT NULL,
    CONSTRAINT tag_pk PRIMARY KEY ( tid )
);

CREATE TABLE terminart (
    taid INTEGER NOT NULL,
    bez  TEXT NOT NULL,
    CONSTRAINT terminart_pk PRIMARY KEY ( taid )
);

CREATE TABLE zeitblock (
    zbid       INTEGER NOT NULL,
    uhrzeitvon DATE NOT NULL,
    uhrzeitbis DATE NOT NULL,
    CONSTRAINT zeitblock_pk PRIMARY KEY ( zbid )
);

-- Tables with level 1 dependencies
CREATE TABLE modul (
    mid           INTEGER NOT NULL,
    bez           TEXT NOT NULL,
    cp            INTEGER NOT NULL,
    regelsemester INTEGER NOT NULL,
    modulart_maid INTEGER NOT NULL,
    CONSTRAINT modul_pk PRIMARY KEY ( mid ),
    CONSTRAINT modul_modulart_fk FOREIGN KEY ( modulart_maid ) REFERENCES modulart ( maid )
);

CREATE TABLE modulbt (
    mbtid            INTEGER NOT NULL,
    modul_mid        INTEGER NOT NULL,
    sws              INTEGER NOT NULL,
    modulbtart_mbaid INTEGER NOT NULL,
    CONSTRAINT modulbt_pk PRIMARY KEY ( mbtid ),
    CONSTRAINT modulbt_modul_fk FOREIGN KEY ( modul_mid ) REFERENCES modul ( mid ),
    CONSTRAINT modulbt_modulbtart_fk FOREIGN KEY ( modulbtart_mbaid ) REFERENCES modulbtart ( mbaid )
);

CREATE TABLE personenrolle (
    prid        INTEGER NOT NULL,
    datumbeginn DATE NOT NULL,
    datumende   DATE,
    person_pid  INTEGER NOT NULL,
    rolle_rid   INTEGER NOT NULL,
    CONSTRAINT personenrolle_pk PRIMARY KEY ( prid ),
    CONSTRAINT personenrolle_person_fk FOREIGN KEY ( person_pid ) REFERENCES person ( pid ),
    CONSTRAINT personenrolle_rolle_fk FOREIGN KEY ( rolle_rid ) REFERENCES rolle ( rid )
);

CREATE TABLE termin (
    tid            INTEGER NOT NULL,
    terminart_taid INTEGER NOT NULL,
    CONSTRAINT termin_pk PRIMARY KEY ( tid ),
    CONSTRAINT termin_terminart_fk FOREIGN KEY ( terminart_taid ) REFERENCES terminart ( taid )
);

-- Tables with level 2 dependencies
CREATE TABLE einzeltermin (
    tid             INTEGER NOT NULL,
    datumuhrzeitvon DATE NOT NULL,
    datumuhrzeitbis DATE NOT NULL,
    CONSTRAINT einzeltermin_pk PRIMARY KEY ( tid ),
    CONSTRAINT einzeltermin_termin_fk FOREIGN KEY ( tid ) REFERENCES termin ( tid )
);

CREATE TABLE kurs (
    kid          INTEGER NOT NULL,
    modul_mid    INTEGER NOT NULL,
    semester_sid INTEGER NOT NULL,
    CONSTRAINT kurs_pk PRIMARY KEY ( kid ),
    CONSTRAINT kurs_modul_fk FOREIGN KEY ( modul_mid ) REFERENCES modul ( mid ),
    CONSTRAINT kurs_semester_fk FOREIGN KEY ( semester_sid ) REFERENCES semester ( sid )
);

CREATE TABLE lehrperson (
    prid         INTEGER NOT NULL,
    datumbeginn  DATE NOT NULL,
    datumende    DATE,
    pid          INTEGER NOT NULL,
    rid          INTEGER NOT NULL,
    steuernummer TEXT NOT NULL,
    CONSTRAINT lehrperson_pk PRIMARY KEY ( prid ),
    CONSTRAINT lehrperson_personenrolle_fk FOREIGN KEY ( prid ) REFERENCES personenrolle ( prid )
);

CREATE TABLE sonstige (
    prid        INTEGER NOT NULL,
    datumbeginn DATE NOT NULL,
    datumende   DATE,
    pid         INTEGER NOT NULL,
    rid         INTEGER NOT NULL,
    CONSTRAINT sonstige_pk PRIMARY KEY ( prid ),
    CONSTRAINT sonstige_personenrolle_fk FOREIGN KEY ( prid ) REFERENCES personenrolle ( prid )
);

CREATE TABLE studentin (
    prid        INTEGER NOT NULL,
    datumbeginn DATE NOT NULL,
    datumende   DATE,
    pid         INTEGER NOT NULL,
    rid         INTEGER NOT NULL,
    matrnr      TEXT NOT NULL,
    CONSTRAINT studentin_pk PRIMARY KEY ( prid ),
    CONSTRAINT studentin_personenrolle_fk FOREIGN KEY ( prid ) REFERENCES personenrolle ( prid )
);

CREATE TABLE wochentermin (
    tid            INTEGER NOT NULL,
    zeitblock_zbid INTEGER NOT NULL,
    tag_tid        INTEGER NOT NULL,
    CONSTRAINT wochentermin_pk PRIMARY KEY ( tid ),
    CONSTRAINT wochentermin_tag_fk FOREIGN KEY ( tag_tid ) REFERENCES tag ( tid ),
    CONSTRAINT wochentermin_termin_fk FOREIGN KEY ( tid ) REFERENCES termin ( tid ),
    CONSTRAINT wochentermin_zeitblock_fk FOREIGN KEY ( zeitblock_zbid ) REFERENCES zeitblock ( zbid )
);

-- Tables with level 3 dependencies
CREATE TABLE kursbt (
    kbtid           INTEGER NOT NULL,
    kurs_kid        INTEGER NOT NULL,
    modulbt_mbtid   INTEGER NOT NULL,
    raum_rid        INTEGER NOT NULL,
    lehrperson_prid INTEGER NOT NULL,
    termin_tid      INTEGER NOT NULL,
    CONSTRAINT kursbt_pk PRIMARY KEY ( kbtid ),
    CONSTRAINT kursbt_kurs_fk FOREIGN KEY ( kurs_kid ) REFERENCES kurs ( kid ),
    CONSTRAINT kursbt_lehrperson_fk FOREIGN KEY ( lehrperson_prid ) REFERENCES lehrperson ( prid ),
    CONSTRAINT kursbt_modulbt_fk FOREIGN KEY ( modulbt_mbtid ) REFERENCES modulbt ( mbtid ),
    CONSTRAINT kursbt_raum_fk FOREIGN KEY ( raum_rid ) REFERENCES raum ( rid ),
    CONSTRAINT kursbt_termin_fk FOREIGN KEY ( termin_tid ) REFERENCES termin ( tid )
);

-- Tables with level 4 dependencies
CREATE TABLE belegung (
    kursbt_kbtid   INTEGER NOT NULL,
    studentin_prid INTEGER NOT NULL,
    CONSTRAINT belegung_pk PRIMARY KEY ( kursbt_kbtid, studentin_prid ),
    CONSTRAINT belegung_kursbt_fk FOREIGN KEY ( kursbt_kbtid ) REFERENCES kursbt ( kbtid ),
    CONSTRAINT belegung_studentin_fk FOREIGN KEY ( studentin_prid ) REFERENCES studentin ( prid )
);

