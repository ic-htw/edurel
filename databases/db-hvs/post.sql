-- =============================================================================
-- Beispieldaten für das Hochschulverwaltungssystem (HVS)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Level 0: Tabellen ohne Abhängigkeiten
-- -----------------------------------------------------------------------------

-- Modularten
INSERT INTO modulart (maid, bez, aktiv, lfdnr) VALUES
(1, 'Pflichtmodul', 'J', 1),
(2, 'Wahlpflichtmodul', 'J', 2),
(3, 'Wahlmodul', 'J', 3),
(4, 'Praxismodul', 'J', 4);

-- Modulbestandteilarten
INSERT INTO modulbtart (mbaid, bez, aktiv, lfdnr) VALUES
(1, 'Vorlesung', 'J', 1),
(2, 'Übung', 'J', 2),
(3, 'Praktikum', 'J', 3),
(4, 'Seminar', 'J', 4),
(5, 'Projekt', 'J', 5);

-- Personen
INSERT INTO person (pid, name) VALUES
(1, 'Prof. Dr. Anna Müller'),
(2, 'Dr. Peter Schmidt'),
(3, 'Prof. Dr. Maria Weber'),
(4, 'Dr. Thomas Klein'),
(5, 'Max Mustermann'),
(6, 'Lisa Wagner'),
(7, 'Tom Fischer'),
(8, 'Sarah Meyer'),
(9, 'Jan Becker'),
(10, 'Nina Schulz'),
(11, 'Claudia Schneider'),
(12, 'Michael Hoffmann');

-- Räume
INSERT INTO raum (rid, raumnr) VALUES
(1, 'A101'),
(2, 'A102'),
(3, 'B201'),
(4, 'B202'),
(5, 'C301'),
(6, 'D401'),
(7, 'E501'),
(8, 'F601');

-- Rollen
INSERT INTO rolle (rid, bez) VALUES
(1, 'Professor'),
(2, 'Dozent'),
(3, 'Student'),
(4, 'Verwaltung'),
(5, 'Dekan');

-- Semester
INSERT INTO semester (sid, bez, beginn, ende, vlbeginn, vlende) VALUES
(1, 'WS 2023/24', '2023-10-01', '2024-03-31', '2023-10-15', '2024-02-15'),
(2, 'SS 2024', '2024-04-01', '2024-09-30', '2024-04-15', '2024-07-31'),
(3, 'WS 2024/25', '2024-10-01', '2025-03-31', '2024-10-15', '2025-02-15');

-- Wochentage
INSERT INTO tag (tid, bez) VALUES
(1, 'Montag'),
(2, 'Dienstag'),
(3, 'Mittwoch'),
(4, 'Donnerstag'),
(5, 'Freitag'),
(6, 'Samstag'),
(7, 'Sonntag');

-- Terminarten
INSERT INTO terminart (taid, bez) VALUES
(1, 'Wöchentlich'),
(2, 'Einzeltermin'),
(3, '14-tägig'),
(4, 'Blockveranstaltung');

-- Zeitblöcke (als DATE gespeichert, aber logisch als Uhrzeit zu verstehen)
INSERT INTO zeitblock (zbid, uhrzeitvon, uhrzeitbis) VALUES
(1, '1970-01-01 08:00:00', '1970-01-01 09:30:00'),
(2, '1970-01-01 10:00:00', '1970-01-01 11:30:00'),
(3, '1970-01-01 12:00:00', '1970-01-01 13:30:00'),
(4, '1970-01-01 14:00:00', '1970-01-01 15:30:00'),
(5, '1970-01-01 16:00:00', '1970-01-01 17:30:00'),
(6, '1970-01-01 18:00:00', '1970-01-01 19:30:00');

-- -----------------------------------------------------------------------------
-- Level 1: Tabellen mit einer Abhängigkeitsebene
-- -----------------------------------------------------------------------------

-- Module
INSERT INTO modul (mid, bez, cp, regelsemester, modulart_maid) VALUES
(1, 'Datenbanken', 6, 3, 1),
(2, 'Programmierung 1', 8, 1, 1),
(3, 'Algorithmen und Datenstrukturen', 6, 2, 1),
(4, 'Softwareengineering', 6, 4, 1),
(5, 'Webentwicklung', 5, 3, 2),
(6, 'Mobile Computing', 5, 5, 2),
(7, 'Projektmanagement', 4, 6, 3);

-- Modulbestandteile
INSERT INTO modulbt (mbtid, modul_mid, sws, modulbtart_mbaid) VALUES
(1, 1, 3, 1),  -- Datenbanken: Vorlesung
(2, 1, 2, 3),  -- Datenbanken: Praktikum
(3, 2, 4, 1),  -- Programmierung 1: Vorlesung
(4, 2, 2, 2),  -- Programmierung 1: Übung
(5, 3, 3, 1),  -- Algorithmen: Vorlesung
(6, 3, 2, 2),  -- Algorithmen: Übung
(7, 4, 3, 1),  -- Softwareengineering: Vorlesung
(8, 4, 1, 4),  -- Softwareengineering: Seminar
(9, 5, 3, 1),  -- Webentwicklung: Vorlesung
(10, 5, 2, 3), -- Webentwicklung: Praktikum
(11, 6, 3, 1), -- Mobile Computing: Vorlesung
(12, 6, 2, 3), -- Mobile Computing: Praktikum
(13, 7, 2, 4), -- Projektmanagement: Seminar
(14, 7, 2, 5); -- Projektmanagement: Projekt

-- Personenrollen
INSERT INTO personenrolle (prid, datumbeginn, datumende, person_pid, rolle_rid) VALUES
(1, '2020-01-01', NULL, 1, 1),  -- Anna Müller: Professor
(2, '2021-03-01', NULL, 2, 2),  -- Peter Schmidt: Dozent
(3, '2019-09-01', NULL, 3, 1),  -- Maria Weber: Professor
(4, '2022-01-01', NULL, 4, 2),  -- Thomas Klein: Dozent
(5, '2023-10-01', NULL, 5, 3),  -- Max Mustermann: Student
(6, '2023-10-01', NULL, 6, 3),  -- Lisa Wagner: Student
(7, '2023-10-01', NULL, 7, 3),  -- Tom Fischer: Student
(8, '2023-10-01', NULL, 8, 3),  -- Sarah Meyer: Student
(9, '2023-10-01', NULL, 9, 3),  -- Jan Becker: Student
(10, '2023-10-01', NULL, 10, 3), -- Nina Schulz: Student
(11, '2018-01-01', NULL, 11, 4), -- Claudia Schneider: Verwaltung
(12, '2017-01-01', NULL, 12, 5); -- Michael Hoffmann: Dekan

-- Termine
INSERT INTO termin (tid, terminart_taid) VALUES
(1, 1),  -- Wöchentlicher Termin
(2, 1),
(3, 1),
(4, 1),
(5, 1),
(6, 1),
(7, 1),
(8, 1),
(9, 1),
(10, 1),
(11, 1),
(12, 1),
(13, 1),
(14, 1),
(15, 2), -- Einzeltermin
(16, 2);

-- -----------------------------------------------------------------------------
-- Level 2: Tabellen mit zwei Abhängigkeitsebenen
-- -----------------------------------------------------------------------------

-- Einzeltermine
INSERT INTO einzeltermin (tid, datumuhrzeitvon, datumuhrzeitbis) VALUES
(15, '2024-01-15 14:00:00', '2024-01-15 17:00:00'),
(16, '2024-02-20 09:00:00', '2024-02-20 16:00:00');

-- Kurse
INSERT INTO kurs (kid, modul_mid, semester_sid) VALUES
(1, 1, 2),  -- Datenbanken im SS 2024
(2, 2, 1),  -- Programmierung 1 im WS 2023/24
(3, 3, 2),  -- Algorithmen im SS 2024
(4, 4, 2),  -- Softwareengineering im SS 2024
(5, 5, 2),  -- Webentwicklung im SS 2024
(6, 1, 3),  -- Datenbanken im WS 2024/25
(7, 6, 3);  -- Mobile Computing im WS 2024/25

-- Lehrpersonen
INSERT INTO lehrperson (prid, datumbeginn, datumende, pid, rid, steuernummer) VALUES
(1, '2020-01-01', NULL, 1, 1, 'DE123456789'),
(2, '2021-03-01', NULL, 2, 2, 'DE987654321'),
(3, '2019-09-01', NULL, 3, 1, 'DE456789123'),
(4, '2022-01-01', NULL, 4, 2, 'DE321654987');

-- Sonstige
INSERT INTO sonstige (prid, datumbeginn, datumende, pid, rid) VALUES
(11, '2018-01-01', NULL, 11, 4),
(12, '2017-01-01', NULL, 12, 5);

-- Studentinnen
INSERT INTO studentin (prid, datumbeginn, datumende, pid, rid, matrnr) VALUES
(5, '2023-10-01', NULL, 5, 3, '1001'),
(6, '2023-10-01', NULL, 6, 3, '1002'),
(7, '2023-10-01', NULL, 7, 3, '1003'),
(8, '2023-10-01', NULL, 8, 3, '1004'),
(9, '2023-10-01', NULL, 9, 3, '1005'),
(10, '2023-10-01', NULL, 10, 3, '1006');

-- Wochentermine
INSERT INTO wochentermin (tid, zeitblock_zbid, tag_tid) VALUES
(1, 1, 1),   -- Montag, 08:00-09:30
(2, 3, 1),   -- Montag, 12:00-13:30
(3, 2, 2),   -- Dienstag, 10:00-11:30
(4, 4, 2),   -- Dienstag, 14:00-15:30
(5, 1, 3),   -- Mittwoch, 08:00-09:30
(6, 3, 3),   -- Mittwoch, 12:00-13:30
(7, 2, 4),   -- Donnerstag, 10:00-11:30
(8, 4, 4),   -- Donnerstag, 14:00-15:30
(9, 1, 5),   -- Freitag, 08:00-09:30
(10, 2, 5),  -- Freitag, 10:00-11:30
(11, 3, 5),  -- Freitag, 12:00-13:30
(12, 4, 5),  -- Freitag, 14:00-15:30
(13, 1, 2),  -- Dienstag, 08:00-09:30
(14, 5, 3);  -- Mittwoch, 16:00-17:30

-- -----------------------------------------------------------------------------
-- Level 3: Tabellen mit drei Abhängigkeitsebenen
-- -----------------------------------------------------------------------------

-- Kursbestandteile
INSERT INTO kursbt (kbtid, kurs_kid, modulbt_mbtid, raum_rid, lehrperson_prid, termin_tid) VALUES
-- Datenbanken SS 2024
(1, 1, 1, 1, 1, 1),   -- Vorlesung mit Prof. Müller
(2, 1, 2, 5, 2, 2),   -- Praktikum mit Dr. Schmidt

-- Programmierung 1 WS 2023/24
(3, 2, 3, 2, 3, 3),   -- Vorlesung mit Prof. Weber
(4, 2, 4, 6, 4, 4),   -- Übung mit Dr. Klein

-- Algorithmen SS 2024
(5, 3, 5, 3, 3, 5),   -- Vorlesung mit Prof. Weber
(6, 3, 6, 7, 4, 6),   -- Übung mit Dr. Klein

-- Softwareengineering SS 2024
(7, 4, 7, 1, 1, 7),   -- Vorlesung mit Prof. Müller
(8, 4, 8, 4, 1, 8),   -- Seminar mit Prof. Müller

-- Webentwicklung SS 2024
(9, 5, 9, 2, 2, 9),   -- Vorlesung mit Dr. Schmidt
(10, 5, 10, 5, 2, 10), -- Praktikum mit Dr. Schmidt

-- Datenbanken WS 2024/25
(11, 6, 1, 1, 1, 11),  -- Vorlesung mit Prof. Müller
(12, 6, 2, 5, 2, 12),  -- Praktikum mit Dr. Schmidt

-- Mobile Computing WS 2024/25
(13, 7, 11, 3, 3, 13), -- Vorlesung mit Prof. Weber
(14, 7, 12, 6, 4, 14); -- Praktikum mit Dr. Klein

-- -----------------------------------------------------------------------------
-- Level 4: Tabellen mit vier Abhängigkeitsebenen
-- -----------------------------------------------------------------------------

-- Belegungen (Studierende belegen Kursbestandteile)
INSERT INTO belegung (kursbt_kbtid, studentin_prid) VALUES
-- Datenbanken SS 2024
(1, 5), (1, 6), (1, 7), (1, 8),
(2, 5), (2, 6), (2, 7), (2, 8),

-- Programmierung 1 WS 2023/24
(3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
(4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10),

-- Algorithmen SS 2024
(5, 5), (5, 6), (5, 9), (5, 10),
(6, 5), (6, 6), (6, 9), (6, 10),

-- Softwareengineering SS 2024
(7, 7), (7, 8),
(8, 7), (8, 8),

-- Webentwicklung SS 2024
(9, 5), (9, 7), (9, 9),
(10, 5), (10, 7), (10, 9),

-- Datenbanken WS 2024/25
(11, 9), (11, 10),
(12, 9), (12, 10),

-- Mobile Computing WS 2024/25
(13, 5), (13, 6), (13, 7), (13, 8),
(14, 5), (14, 6), (14, 7), (14, 8);
