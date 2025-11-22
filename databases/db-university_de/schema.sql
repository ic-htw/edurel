CREATE TABLE semester (
    sid INTEGER,
    bez VARCHAR NOT NULL,
    PRIMARY KEY (sid)
);


CREATE TABLE modul (
    mid INTEGER,
    bez VARCHAR NOT NULL,
    PRIMARY KEY (mid)
);


CREATE TABLE kurs (
    kid INTEGER,
    sid INTEGER NOT NULL,
    mid INTEGER NOT NULL,
    PRIMARY KEY (kid),
    CONSTRAINT fk_kurs_semester
        FOREIGN KEY (sid)
        REFERENCES semester(sid),        
    CONSTRAINT fk_kurs_modul
        FOREIGN KEY (mid)
        REFERENCES modul(mid)        
);


