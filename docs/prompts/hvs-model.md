# Hochschulverwaltungssystem - HVS
- Erstelle ein relationales Datenmdell für die Verwaltung einer Hochschule

## Bereiche der Modellierung
- Personen
- Standorte
- Akademische Struktur
- Lehre
- Prüfungen
- Bibliothek

## Personen
- Unterschiedliche Personengruppen mit unterschiedlichen Aufgaben
- Studendierende sind Studiengängen zugeordnet, studieren nach einer Studienordnung, nehmen an Lehrveranstaltungen teil, machen Prüfungen
- Lehrpersonen halten Lehrveranstaltungen, führen Prüfungen durch
- Lehrpersonen (Rollen): Professoren, akademische Mitarbeiter, Lehrbeauftragte
- Rollen gelten für bestimmte Zeiträume

## Standorte
- Eine Hochschule umfasst mehrere Standorte
- Ein Standort umfasst Gebäude
- Ein Gebäude enthält Räume
- Räume haben verschiedene Raumarten
- Räume haben Ausstattungsmerkmale, z.B. Whiteboard, Beamer

## Akademische Struktur
- Eine Hochschule setzt sich aus Fachbereichen zusammen
- Ein Fachbereich beinhaltet Studiengänge
- Ein Studiengang hat mehrere Studienordnungen
- Studienordnungen legen Module und deren Regelsemester fest
- Module können Pflicht, Wahlpficht und Wahl sein
- Module haben Bestandteile, z.B. Vorlesung, Übung
- Bestandteile haben einen zeitlichen Umfang (SWS)

## Lehre
- Studierende belegen Module
- Module werden semesterweise durchgeführt
- Module können im Semester mehrfach angeboten werden (Züge, Gruppen)
- Modulbestandteile finden zu bestimmten Zeiten in festgelegten Räumen statt
- Z.B. wochenweise in bestimmten Zeitbereichen
- Oder zweiwöchentlich, oder als Blockveranstaltung
- Belegungen haben Prioritäten, z.B Studierende mit Kindern
- Oder Belegung im Regelsemester

## Prüfungen
- Studierende melden sich zu Prüfungen an
- Prüfungen beziehen sich auf Module
- Haben einen Status, z.B. angemeldet, abgemeldet, durchgeführt
- Haben einen Termin
- Führen zu einer Note

## Bibliothek
- Die Bibliothek hat verschiedene Medien, z.B. Bücher, Zeitschriften, Abschlussarbeiten
- Medien werden Schlagworte zugeordnet
- Zu jedem Medium gibt es Exemplare, die an verschiedenen Standorten stehen können
- Exemplare können zu unterschiedlichen Zeitpunkten beschafft worden sein
- Es gibt mehrere Nutzerklassen, z.B. Studierende, ProfessorInnen
- Für die Nutzerklassen gelten unterschiedliche Ausleihefristen
- Ausleihen können verlängert werden
- Medien können vorbestellt werden
- Bei Fristüberschreitung erfolgt eine Mahnung

