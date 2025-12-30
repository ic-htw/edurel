CREATE TABLE roomkind (
    rkid INTEGER NOT NULL,
    descr  VARCHAR NOT NULL,
    CONSTRAINT roomkind_pk PRIMARY KEY (rkid)
);

CREATE TABLE equipmentkind (
    ekid INTEGER NOT NULL,
    descr  VARCHAR NOT NULL,
    CONSTRAINT equipmentkind_pk PRIMARY KEY (ekid)
);

CREATE TABLE building (
    bid      INTEGER NOT NULL,
    descr      VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    CONSTRAINT building_pk PRIMARY KEY (bid)
);

CREATE TABLE room (
    rid         INTEGER NOT NULL,
    roomno      VARCHAR NOT NULL,
    noofseats   INTEGER NOT NULL,
    bid         INTEGER NOT NULL,
    rkid        INTEGER NOT NULL,
    CONSTRAINT room_pk PRIMARY KEY (rid),
    CONSTRAINT room_building_fk FOREIGN KEY (bid) 
      REFERENCES building (bid),
    CONSTRAINT room_roomkind_fk FOREIGN KEY (rkid)
      REFERENCES roomkind (rkid)
);

CREATE TABLE equipment (
    rid    INTEGER NOT NULL,
    ekid   INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    CONSTRAINT equipment_pk PRIMARY KEY (rid, ekid),
    CONSTRAINT equipment_equipmentkind_fk FOREIGN KEY (ekid)
      REFERENCES equipmentkind (ekid),
    CONSTRAINT equipment_room_fk FOREIGN KEY (rid)
      REFERENCES room (rid)
);


CREATE TABLE staging (
    roomno      VARCHAR,
    noofseats   VARCHAR,
    equipment   VARCHAR,
    kind        VARCHAR,
    building    VARCHAR,
    location    VARCHAR
);
