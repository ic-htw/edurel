
-- PERSONEN
CREATE TABLE person (
  person_id SERIAL PRIMARY KEY,
  vorname VARCHAR(100),
  nachname VARCHAR(100),
  geburtsdatum DATE,
  email VARCHAR(200),
  adresse TEXT
);

CREATE TABLE rolle (
  rolle_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(50) NOT NULL
);

CREATE TABLE person_rolle (
  person_rolle_id SERIAL PRIMARY KEY,
  person_id INT REFERENCES person(person_id),
  rolle_id INT REFERENCES rolle(rolle_id),
  gueltig_von DATE,
  gueltig_bis DATE
);

CREATE TABLE studierender (
  studierender_id SERIAL PRIMARY KEY,
  person_id INT UNIQUE REFERENCES person(person_id),
  matrikelnummer VARCHAR(20) UNIQUE
);

CREATE TABLE lehrperson (
  lehrperson_id SERIAL PRIMARY KEY,
  person_id INT UNIQUE REFERENCES person(person_id)
);

-- STANDORTE
CREATE TABLE standort (
  standort_id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  adresse TEXT
);

CREATE TABLE gebaeude (
  gebaeude_id SERIAL PRIMARY KEY,
  standort_id INT REFERENCES standort(standort_id),
  bezeichnung VARCHAR(50)
);

CREATE TABLE raumart (
  raumart_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(50)
);

CREATE TABLE raum (
  raum_id SERIAL PRIMARY KEY,
  gebaeude_id INT REFERENCES gebaeude(gebaeude_id),
  raumart_id INT REFERENCES raumart(raumart_id),
  raumnummer VARCHAR(20),
  kapazitaet INT
);

CREATE TABLE ausstattung (
  ausstattung_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(50)
);

CREATE TABLE raum_ausstattung (
  raum_id INT REFERENCES raum(raum_id),
  ausstattung_id INT REFERENCES ausstattung(ausstattung_id),
  PRIMARY KEY (raum_id, ausstattung_id)
);

-- AKADEMISCHE STRUKTUR
CREATE TABLE fachbereich (
  fachbereich_id SERIAL PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE studiengang (
  studiengang_id SERIAL PRIMARY KEY,
  fachbereich_id INT REFERENCES fachbereich(fachbereich_id),
  name VARCHAR(100),
  abschluss VARCHAR(20)
);

CREATE TABLE studienordnung (
  studienordnung_id SERIAL PRIMARY KEY,
  studiengang_id INT REFERENCES studiengang(studiengang_id),
  version VARCHAR(20),
  gueltig_ab DATE
);

CREATE TABLE modul (
  modul_id SERIAL PRIMARY KEY,
  modulnummer VARCHAR(20),
  name VARCHAR(100),
  typ VARCHAR(20),
  credits INT
);

CREATE TABLE studienordnung_modul (
  studienordnung_id INT REFERENCES studienordnung(studienordnung_id),
  modul_id INT REFERENCES modul(modul_id),
  regelsemester INT,
  PRIMARY KEY (studienordnung_id, modul_id)
);

CREATE TABLE modulbestandteil (
  bestandteil_id SERIAL PRIMARY KEY,
  modul_id INT REFERENCES modul(modul_id),
  typ VARCHAR(50),
  sws INT
);

-- LEHRE
CREATE TABLE semester (
  semester_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(20),
  startdatum DATE,
  enddatum DATE
);

CREATE TABLE modulangebot (
  angebot_id SERIAL PRIMARY KEY,
  modul_id INT REFERENCES modul(modul_id),
  semester_id INT REFERENCES semester(semester_id),
  gruppe VARCHAR(20)
);

CREATE TABLE lehrperson_modulangebot (
  angebot_id INT REFERENCES modulangebot(angebot_id),
  lehrperson_id INT REFERENCES lehrperson(lehrperson_id),
  PRIMARY KEY (angebot_id, lehrperson_id)
);

CREATE TABLE veranstaltungstermin (
  termin_id SERIAL PRIMARY KEY,
  bestandteil_id INT REFERENCES modulbestandteil(bestandteil_id),
  angebot_id INT REFERENCES modulangebot(angebot_id),
  raum_id INT REFERENCES raum(raum_id),
  rhythmus VARCHAR(20),
  wochentag VARCHAR(10),
  uhrzeit_von TIME,
  uhrzeit_bis TIME
);

CREATE TABLE modulbelegung (
  belegung_id SERIAL PRIMARY KEY,
  studierender_id INT REFERENCES studierender(studierender_id),
  angebot_id INT REFERENCES modulangebot(angebot_id),
  prioritaet INT,
  belegungsgrund VARCHAR(50)
);

-- PRÜFUNGEN
CREATE TABLE pruefung (
  pruefung_id SERIAL PRIMARY KEY,
  modul_id INT REFERENCES modul(modul_id),
  semester_id INT REFERENCES semester(semester_id),
  pruefungsdatum DATE,
  status VARCHAR(20)
);

CREATE TABLE pruefungsanmeldung (
  anmeldung_id SERIAL PRIMARY KEY,
  pruefung_id INT REFERENCES pruefung(pruefung_id),
  studierender_id INT REFERENCES studierender(studierender_id),
  anmeldedatum DATE,
  note NUMERIC(3,1)
);

-- BIBLIOTHEK
CREATE TABLE medium (
  medium_id SERIAL PRIMARY KEY,
  titel VARCHAR(200),
  medientyp VARCHAR(50),
  erscheinungsjahr INT
);

CREATE TABLE schlagwort (
  schlagwort_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(50)
);

CREATE TABLE medium_schlagwort (
  medium_id INT REFERENCES medium(medium_id),
  schlagwort_id INT REFERENCES schlagwort(schlagwort_id),
  PRIMARY KEY (medium_id, schlagwort_id)
);

CREATE TABLE exemplar (
  exemplar_id SERIAL PRIMARY KEY,
  medium_id INT REFERENCES medium(medium_id),
  standort_id INT REFERENCES standort(standort_id),
  anschaffungsdatum DATE,
  status VARCHAR(20)
);

CREATE TABLE nutzerklasse (
  nutzerklasse_id SERIAL PRIMARY KEY,
  bezeichnung VARCHAR(50),
  leihfrist_tage INT
);

CREATE TABLE bibliotheksnutzer (
  nutzer_id SERIAL PRIMARY KEY,
  person_id INT REFERENCES person(person_id),
  nutzerklasse_id INT REFERENCES nutzerklasse(nutzerklasse_id)
);

CREATE TABLE ausleihe (
  ausleihe_id SERIAL PRIMARY KEY,
  exemplar_id INT REFERENCES exemplar(exemplar_id),
  nutzer_id INT REFERENCES bibliotheksnutzer(nutzer_id),
  ausleihdatum DATE,
  faellig_am DATE,
  rueckgabedatum DATE,
  verlaengerungen INT
);

CREATE TABLE vormerkung (
  vormerkung_id SERIAL PRIMARY KEY,
  medium_id INT REFERENCES medium(medium_id),
  nutzer_id INT REFERENCES bibliotheksnutzer(nutzer_id),
  datum DATE
);

CREATE TABLE mahnung (
  mahnung_id SERIAL PRIMARY KEY,
  ausleihe_id INT REFERENCES ausleihe(ausleihe_id),
  mahnstufe INT,
  mahn_datum DATE
);
```
