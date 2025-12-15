create table Prompt (
  pid integer not null,
  tag text not null,
  lang text not null,
  db text not null,
  prompt text not null,
  constraint pk_prompt primary key (pid),
);

create sequence Execution_eid_seq start with 1;

create table Execution (
  eid integer not null default nextval('Execution_eid_seq'),
  ts timestamp not null,
  sql text not null,
  model text not null,
  pid integer not null,
  constraint pk_execution primary key (eid),
  constraint fk_prompt foreign key (pid) references Prompt(pid)
);

