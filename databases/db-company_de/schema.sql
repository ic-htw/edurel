create table Orgeinheit (
  OEID integer not null,
  Leitung integer,
  Obereinheit integer,
  Bezeichnung varchar not null,
  constraint PK_Orgeinheit primary key (OEID),
  -- constraint FK_LEITUNG foreign key (Leitung) references Mitarbeiter
);

create table Mitarbeiter (
  MID integer not null,
  OEID integer not null,
  Name varchar not null,
  Vorname varchar not null,
  Eintrittsdatum date not null,
  Gehalt decimal(9,2) not null,
  Bonus decimal(9,2),
  constraint PK_Mitarbeiter primary key (MID),
  constraint CHK_Gehalt check(Gehalt > 15000),
  constraint FK_MA_ABT foreign key (OEID) references Orgeinheit
);

create table Projekt (
  PID integer not null,
  Titel varchar not null,
  Budget decimal(13,2),
  constraint PK_Projekt primary key (PID)
);


create table MaProj (
  MID integer not null,
  PID integer not null,
  StdProWoche integer not null,
  constraint PK_MaProj primary key (MID, PID),
  constraint FK_MAPROJ1 foreign key (MID) references Mitarbeiter,
  constraint FK_MAPROJ2 foreign key (PID) references Projekt
);
