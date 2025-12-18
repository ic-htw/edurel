<!-------------------------------------------------------------------------------------------------->
<!-- Kursübersicht mit Studierendenanzahl -->
<!-------------------------------------------------------------------------------------------------->

### erstelle eine abfrage, die folgende spalten hat
- Bez - von Semester
- Bez - von Modul
- Bez - von Modulart
- Bez - von ModulBTArt
- SWS - von ModulBT
- RaumNr - von Raum
- Bez - von Tag
- UhrzeitVon - von Zeitblock
- UhrzeitBis - von Zeitblock
- Anzahl_Studierende

gruppiere nach allen spalten bis auf Anzahl_Studierende

-- Kursübersicht mit Studierendenanzahl
SELECT
    sem.bez AS semester_bez,
    mod.bez AS modul_bez,
    ma.bez AS modulart_bez,
    mba.bez AS modulbtart_bez,
    mb.sws AS sws,
    r.raumnr AS raumnr,
    t.bez AS tag_bez,
    zb.uhrzeitvon AS uhrzeitvon,
    zb.uhrzeitbis AS uhrzeitbis,
    COUNT(b.studentin_prid) AS anzahl_studierende
FROM kursbt kb
    JOIN kurs k ON kb.kurs_kid = k.kid
    JOIN semester sem ON k.semester_sid = sem.sid
    JOIN modul mod ON k.modul_mid = mod.mid
    JOIN modulart ma ON mod.modulart_maid = ma.maid
    JOIN modulbt mb ON kb.modulbt_mbtid = mb.mbtid
    JOIN modulbtart mba ON mb.modulbtart_mbaid = mba.mbaid
    JOIN raum r ON kb.raum_rid = r.rid
    JOIN termin ter ON kb.termin_tid = ter.tid
    JOIN wochentermin wt ON ter.tid = wt.tid
    JOIN tag t ON wt.tag_tid = t.tid
    JOIN zeitblock zb ON wt.zeitblock_zbid = zb.zbid
    LEFT JOIN belegung b ON kb.kbtid = b.kursbt_kbtid
GROUP BY
    sem.bez,
    mod.bez,
    ma.bez,
    mba.bez,
    mb.sws,
    r.raumnr,
    t.bez,
    zb.uhrzeitvon,
    zb.uhrzeitbis
ORDER BY
    sem.bez DESC,
    t.bez,

<!-------------------------------------------------------------------------------------------------->
<!-- Personenübersicht mit Rollen -->
<!-------------------------------------------------------------------------------------------------->

### erstelle eine abfrage, die folgende spalten hat
- Name - von Person
- DatumBeginn - von Personenrolle
- DatumEnde - von Personenrolle
- Bez - von Rolle
- MatrNr - von Studentin 
- Steuernummer - von Lehrperson 

-- Personenübersicht mit Rollen
SELECT
    p.name AS name,
    pr.datumbeginn AS datumbeginn,
    pr.datumende AS datumende,
    r.bez AS rolle_bez,
    s.matrnr AS matrnr,
    l.steuernummer AS steuernummer
FROM personenrolle pr
    JOIN person p ON pr.person_pid = p.pid
    JOIN rolle r ON pr.rolle_rid = r.rid
    LEFT JOIN studentin s ON pr.prid = s.prid
    LEFT JOIN lehrperson l ON pr.prid = l.prid
ORDER BY
    p.name,
    pr.datumbeginn DESC;
