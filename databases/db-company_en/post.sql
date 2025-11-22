insert into OrgUnit values (11, null, null, 'Company');
insert into OrgUnit values (12, null, 11, 'Administration');
insert into OrgUnit values (13, null, 12, 'HR');
insert into OrgUnit values (14, null, 12, 'Accounting');
insert into OrgUnit values (15, null, 11, 'Production');
insert into OrgUnit values (16, null, 15, 'Plant');
insert into OrgUnit values (17, null, 15, 'Warehouse');

insert into Employee values (101, 11, 'Patil', '2000-05-01', 180000, null);
insert into Employee values (102, 12, 'Durmaz', '2005-07-01', 120000, null);
insert into Employee values (103, 13, 'Blaschke', '2002-11-01', 93000, null);
insert into Employee values (104, 13, 'Stone', '2006-06-01', 42000, null);
insert into Employee values (105, 13, 'Dalal', '2018-02-02', 38000, 1000);
insert into Employee values (106, 14, 'Li', '2002-12-01', 89000, null);
insert into Employee values (107, 14, 'Nguyen', '2006-07-01', 41000, null);
insert into Employee values (108, 14, 'Sanchez', '2014-04-01', 39000, 1500);
insert into Employee values (109, 15, 'Umarani', '2006-07-01', 142000, null);
insert into Employee values (110, 16, 'Ortega', '2005-09-02', 90000, null);
insert into Employee values (111, 16, 'Doshi', '2010-01-02', 42000, null);
insert into Employee values (112, 16, 'Singh', '2012-03-01', 43000, 2100);
insert into Employee values (113, 16, 'Jadhav', '2001-08-01', 91000, null);
insert into Employee values (114, 17, 'Popov', '2009-03-02', 34000, null);
insert into Employee values (115, 17, 'Kumar', '2013-05-01', 32000, null);
insert into Employee values (116, 17, 'Krause', '2011-08-01', 31000, null);
insert into Employee values (117, 17, 'Oezdem', '2014-08-01', 33000, 1900);
insert into Employee values (118, 17, 'Okeke', '2013-11-01', 32000, 1900);


insert into Project values (1, 'Strategy', 80000);
insert into Project values (2, 'CRM', 20000);
insert into Project values (3, 'Plant Restructurierung', 50000);
insert into Project values (4, 'Sales', null);

insert into EmpProj values (101, 1, 4);
insert into EmpProj values (102, 1, 4);
insert into EmpProj values (109, 1, 4);
insert into EmpProj values (102, 2, 4);
insert into EmpProj values (103, 2, 8);
insert into EmpProj values (109, 3, 2);
insert into EmpProj values (114, 3, 4);
insert into EmpProj values (117, 3, 4);
insert into EmpProj values (118, 3, 8);


update OrgUnit set Head = 101 where OUID=11;
update OrgUnit set Head = 102 where OUID=12;
update OrgUnit set Head = 103 where OUID=13;
update OrgUnit set Head = 106 where OUID=14;
update OrgUnit set Head = 109 where OUID=15;
update OrgUnit set Head = 110 where OUID=16;
update OrgUnit set Head = 109 where OUID=17;
