create table OrgUnit (
  OUID integer not null,
  Head integer,
  SuperUnit integer,
  Name varchar not null,
  constraint PK_OrgUnit primary key (OUID)
  -- constraint FK_Head foreign key (Head) references Employee(EID)
);

create table Employee (
  EID integer not null,
  OUID integer not null,
  LastName varchar not null,
  Hiredate date not null,
  Salary decimal(9,2) not null,
  Bonus decimal(9,2),
  constraint PK_Employee primary key (EID),
  constraint CHK_Salary check(Salary > 15000),
  constraint FK_OrgUnit foreign key (OUID) references OrgUnit
);

create table Project (
  PID integer not null,
  Title varchar not null,
  Budget decimal(13,2),
  constraint PK_Project primary key (PID)
);


create table EmpProj (
  EID integer not null,
  PID integer not null,
  NoOfHoursPerWeek integer not null,
  constraint PK_EmpProj primary key (EID, PID),
  constraint FK_EmpProj1 foreign key (EID) references Employee,
  constraint FK_EmpProj2 foreign key (PID) references Project
);

