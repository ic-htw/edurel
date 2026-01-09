create table Playlist (
  PLID         integer       not null,
  Name         text not null,
  LetzterAbruf date          null,
  constraint pk_playlist primary key(PLID)
);

create table Genre (
  GID         integer       not null,
  Bezeichnung text  not null,
  constraint pk_genre primary key(GID)
);

create table Stueck (
  SID         integer       not null,
  Titel       text  not null,
  DauerInSek  integer       not null,
  PLID        integer       not null,
  GID         integer       not null,
  constraint pk_stueck primary key(SID),
  constraint fk_playlist foreign key (PLID) references Playlist,
  constraint fk_genre foreign key (GID) references Genre
);


