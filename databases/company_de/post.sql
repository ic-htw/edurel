insert into Orgeinheit values (11, null, null, 'Unternehmen');
insert into Orgeinheit values (12, null, 11, 'Verwaltung');
insert into Orgeinheit values (13, null, 12, 'Personal');
insert into Orgeinheit values (14, null, 12, 'Buchhaltung');
insert into Orgeinheit values (15, null, 11, 'Produktion');
insert into Orgeinheit values (16, null, 15, 'Werk');
insert into Orgeinheit values (17, null, 15, 'Lager');

insert into Mitarbeiter values (101, 11, 'Kramer', 'Sabine', '2000-05-01', 180000, null);
insert into Mitarbeiter values (102, 12, 'Durmaz', 'Guel', '2005-07-01', 120000, null);
insert into Mitarbeiter values (103, 13, 'Blaschke', 'Jens', '2002-11-01', 93000, null);
insert into Mitarbeiter values (104, 13, 'Rot', 'Ralf', '2006-06-01', 42000, null);
insert into Mitarbeiter values (105, 13, 'Neumann', 'Lisa', '2018-02-02', 38000, 1000);
insert into Mitarbeiter values (106, 14, 'Hansen', 'Frauke', '2002-12-01', 89000, null);
insert into Mitarbeiter values (107, 14, 'Nguyen', 'Anh', '2006-07-01', 41000, null);
insert into Mitarbeiter values (108, 14, 'Vogel', 'Henrik', '2014-04-01', 39000, 1500);
insert into Mitarbeiter values (109, 15, 'Meier', 'Hans', '2006-07-01', 142000, null);
insert into Mitarbeiter values (110, 16, 'Schrader', 'Christian', '2005-09-02', 90000, null);
insert into Mitarbeiter values (111, 16, 'Dragovic', 'Milan', '2010-01-02', 42000, null);
insert into Mitarbeiter values (112, 16, 'Hensen', 'Klaus', '2012-03-01', 43000, 2100);
insert into Mitarbeiter values (113, 16, 'Schimmel', 'Alfred', '2001-08-01', 91000, null);
insert into Mitarbeiter values (114, 17, 'Popov', 'Iwan', '2009-03-02', 34000, null);
insert into Mitarbeiter values (115, 17, 'Hermans', 'Fred', '2013-05-01', 32000, null);
insert into Mitarbeiter values (116, 17, 'Krause', 'Frank', '2011-08-01', 31000, null);
insert into Mitarbeiter values (117, 17, 'Oezdem', 'Demir', '2014-08-01', 33000, 1900);
insert into Mitarbeiter values (118, 17, 'Okeke', 'Abeni', '2013-11-01', 32000, 1900);


insert into Projekt values (1, 'Strategie', 80000);
insert into Projekt values (2, 'CRM', 20000);
insert into Projekt values (3, 'Restrukturierung Lager', 50000);
insert into Projekt values (4, 'Vertrieb', null);

insert into MaProj values (101, 1, 4);
insert into MaProj values (102, 1, 4);
insert into MaProj values (109, 1, 4);
insert into MaProj values (102, 2, 4);
insert into MaProj values (103, 2, 8);
insert into MaProj values (109, 3, 2);
insert into MaProj values (114, 3, 4);
insert into MaProj values (117, 3, 4);
insert into MaProj values (118, 3, 8);


update Orgeinheit set Leitung = 101 where OEID=11;
update Orgeinheit set Leitung = 102 where OEID=12;
update Orgeinheit set Leitung = 103 where OEID=13;
update Orgeinheit set Leitung = 106 where OEID=14;
update Orgeinheit set Leitung = 109 where OEID=15;
update Orgeinheit set Leitung = 110 where OEID=16;
update Orgeinheit set Leitung = 109 where OEID=17;
