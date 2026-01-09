create table Playlist (
  PLID         integer       not null,
  Name         text not null,
  LastCall     date          null,
  constraint pk_playlist primary key(PLID)
);

create table Genre (
  GID         integer       not null,
  Description text  not null,
  constraint pk_genre primary key(GID)
);

create table Title (
  TID           integer       not null,
  Name          text  not null,
  DurationInSec integer       not null,
  PLID          integer       not null,
  GID           integer       not null,
  constraint pk_stueck primary key(TID),
  constraint fk_playlist foreign key (PLID) references Playlist,
  constraint fk_genre foreign key (GID) references Genre
);


