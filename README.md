# Studien-Dashboard

Ein Python-Prototyp für die Kommandozeile auf Grundlage der Gesamtarchitektur aus Phase 2. Das Dashboard zeigt den ECTS-gewichteten Notendurchschnitt, Best und Worst Case sowie den Studienfortschritt. Semester, Module und Prüfungsleistungen lassen sich über ein nummeriertes Menü verwalten.

## Installation und erster Start

Die folgenden fünf Schritte entsprechen der separaten Installationsanleitung im Portfolio.

### 1. Python installieren

Du brauchst **Python 3.10 oder neuer**. Falls Python noch nicht installiert ist, kannst Du es über [python.org](https://www.python.org/downloads/) herunterladen und installieren. Es werden ausschließlich Module der Python-Standardbibliothek verwendet. Zusätzliche Pakete sind nicht nötig.

### 2. Programm herunterladen und entpacken

Öffne das [GitHub-Repository](https://github.com/patrick-fuchs/python-abgabe) und wähle **Code → Download ZIP**. Entpacke die ZIP-Datei vollständig, unter Windows über **Alle extrahieren**. Öffne danach den entpackten Ordner, in dem `main.py` liegt. Die übrigen sechs Python-Dateien müssen im selben Ordner bleiben.

### 3. Python-Version prüfen

**Windows:** Öffne im Explorer den Ordner mit `main.py`. Gib in die Adresszeile `powershell` ein und drücke Enter. Prüfe im geöffneten Terminal die Python-Version:

```powershell
py -3 --version
```

Falls `py` nicht erkannt wird, verwende:

```powershell
python --version
```

**macOS:** Öffne ein Terminal im Ordner mit `main.py` und prüfe die Version mit:

```bash
python3 --version
```

Die angezeigte Version muss jeweils mindestens **3.10** sein.

### 4. Programm starten

**Windows:** Gib im geöffneten Terminal folgenden Befehl ein und drücke Enter:

```powershell
py -3 main.py
```

Falls Du die Version mit `python` geprüft hast, verwende stattdessen:

```powershell
python main.py
```

**macOS:** Starte die Anwendung mit:

```bash
python3 main.py
```

Der Startpunkt ist immer `main.py`. Dateien wie `app.py`, `domain.py` oder `view.py` definieren Klassen und Funktionen; ihr direktes Ausführen startet das Dashboard nicht. Auch in VS Code kannst Du die genannten Befehle im integrierten Terminal verwenden. Die Bedienung erfolgt über das Terminal.

### 5. Erste Einträge anlegen

Beim ersten Start ist noch kein Studiengang angelegt. Wähle nacheinander die folgenden Menüpunkte und bestätige jede Eingabe mit Enter:

| Menüpunkt | Eingabe |
| --- | --- |
| **2** | Studiengang anlegen |
| **5** | Semester hinzufügen |
| **8** | Modul hinzufügen |
| **12** | Prüfungsleistung hinzufügen |

Die Zielnote **2,3** und **180 Gesamt-ECTS** werden beim Anlegen vorgeschlagen und können angepasst werden. In Auswahllisten gibst Du die links angezeigte **Auswahlnummer** ein. Mit **0** beendest Du das Programm.

Jede erfolgreiche Änderung wird automatisch im Ordner `daten/` neben `main.py` gespeichert. Dieser Ordner wird beim ersten Speichern angelegt. Beim nächsten Start werden Deine gespeicherten Daten wieder geladen. Der Programmordner muss deshalb beschreibbar sein.

## Bedienung

- **1** zeigt das Dashboard erneut an.
- **2** legt den Studiengang an, sofern noch keiner vorhanden ist.
- **3** bearbeitet die Stammdaten des vorhandenen Studiengangs.
- **4** löscht den Studiengang einschließlich seiner leeren Semester.
- **5–7** fügen Semester hinzu, ändern ihre Nummer oder löschen leere Semester.
- **8–11** fügen Module hinzu, bearbeiten sie, verschieben sie oder löschen sie einschließlich ihrer Prüfungsleistungen.
- **12–14** fügen Prüfungsleistungen hinzu, bearbeiten sie oder löschen sie.
- **0** beendet das Programm.

Bei einer Auswahlliste gibst Du die links angezeigte **Auswahlnummer** ein. Beim Bearbeiten übernimmt eine leere Eingabe mit Enter den bisherigen Wert. Für Noten kannst Du ein Dezimalkomma oder einen Dezimalpunkt verwenden. Prüfungsdaten werden als `TT.MM.JJJJ` oder `JJJJ-MM-TT` eingegeben.

Jede erfolgreiche Änderung wird sofort gespeichert. Löschungen müssen mit `ja` oder `j` bestätigt werden. Bei ungültigen Eingaben erscheint eine verständliche Meldung und das Menü wird erneut angezeigt. Beende das Programm über Menüpunkt **0**.

## Beispiel: Studiengang und erste Note

Das folgende Beispiel beginnt mit einem leeren Datenbestand. Jede einzelne Eingabe in der Tabelle wird mit Enter bestätigt.

| Menüpunkt | Eingaben in dieser Reihenfolge |
| --- | --- |
| **2** – Studiengang anlegen | `Informatik` → `Bachelor of Science` → `2,3` → `180` |
| **5** – Semester hinzufügen | `1` |
| **8** – Modul hinzufügen | Semesterauswahl `1` → `Programmierung` → `5` |
| **12** – Prüfungsleistung hinzufügen | Modulauswahl `1` → `10.10.2026` → `1,7` |

Danach zeigt das Dashboard den aktuellen Schnitt **1,7**, einen Best Case von **1,0** und einen Worst Case von **3,9**. Der Studienfortschritt lautet **5 Punkte (3%)**. Im ersten Semester steht das Modul Programmierung mit der Note 1,7.

### Zweites Modul und ECTS-Gewichtung

Ergänze im selben Studiengang ein weiteres Modul mit einer Prüfung:

| Menüpunkt | Eingaben in dieser Reihenfolge |
| --- | --- |
| **8** – Modul hinzufügen | Semesterauswahl `1` → `Datenbanken` → `10` |
| **12** – Prüfungsleistung hinzufügen | Modulauswahl `1` → `11.10.2026` → `2,3` |

Bei dieser Modulauswahl ist **Datenbanken die Nummer 1** und Programmierung die Nummer 2. Die Auswahl ist alphabetisch sortiert. Orientiere Dich bei vorhandenen eigenen Daten immer an der angezeigten Liste.

Das Modul Datenbanken hat doppelt so viele ECTS wie Programmierung und geht deshalb mit dem doppelten Gewicht in den Schnitt ein:

```text
(5 × 1,7 + 10 × 2,3) / 15 = 2,1
```

| Anzeige | Ergebnis nach beiden Prüfungen |
| --- | --- |
| Aktueller Schnitt | **2,1** |
| Best Case | **1,1** |
| Worst Case | **3,8** |
| Erreichte ECTS und Fortschritt | **15 Punkte (8%)** |

Erfasst Du später eine weitere Prüfung für dasselbe Modul, zählt für die aktuelle Bewertung das neueste Prüfungsdatum. Die Modul-ECTS werden dabei nur einmal gezählt.

## Berechnungsregeln

Die Anwendung bildet die folgenden Regeln des Entwurfs ab:

1. Die aktuelle Note eines Moduls stammt aus der Prüfungsleistung mit dem **neuesten Prüfungsdatum**. Die Reihenfolge der Eingabe spielt dabei keine Rolle.
2. Noten von **1,0 bis 4,0** gelten als bestanden. **5,0** bedeutet nicht bestanden. Die Zielnote liegt zwischen 1,0 und 4,0.
3. Nur aktuell bestandene Module liefern erreichte ECTS und fließen in den aktuellen Schnitt ein. Wiederholungsprüfungen führen nicht zu einer doppelten Zählung.
4. Der aktuelle Schnitt wird nach ECTS gewichtet: `Summe(Note × Modul-ECTS) / erreichte ECTS`. Ohne bestandene Module erscheint `--`.
5. Offene ECTS sind `Gesamt-ECTS − erreichte ECTS`. Im Best Case werden sie mit **1,0**, im Worst Case mit **4,0** gewichtet. Dazu gehören auch ECTS von Modulen, die noch nicht angelegt wurden.
6. Im Dashboard werden Noten auf eine Nachkommastelle und der Fortschritt auf ganze Prozent gerundet. Auswahllisten für Prüfungsleistungen zeigen zwei Nachkommastellen. Berechnungen, Zielvergleiche und gespeicherte Werte bleiben ungerundet.

Die Darstellung folgt dem ASCII-Entwurf aus Phase 1: Studiengang und Abschluss stehen zentriert zwischen zwei Linien. Darunter steht der eingerahmte aktuelle Schnitt zwischen Best und Worst Case. Die erreichten ECTS erscheinen beispielsweise als `30 Punkte (17%)`. Unter der Überschrift `Module` trennt eine Linie jedes Semester von seinen Modulen. Lange Titel und Modulnamen werden innerhalb der 78 Zeichen breiten Anzeige umgebrochen. `--` kennzeichnet Module ohne Prüfung, `5,0` eine nicht bestandene Prüfung. Die Zielnote wird beim Anlegen oder Bearbeiten des Studiengangs festgelegt.

Semester werden absteigend nach ihrer Nummer angezeigt. Innerhalb eines Semesters folgen zuerst Module mit Prüfungen, absteigend nach ihrem neuesten Prüfungsdatum. Bei gleichem Datum entscheidet der Modulname. Danach erscheinen Module ohne Prüfung alphabetisch. Prüfungsdaten und einzelne Modul-ECTS werden nur bei der Verwaltung benötigt und nicht zusätzlich auf dem Dashboard angezeigt.

## Zuordnung und Löschung

- Jedes gespeicherte Semester gehört zu genau einem Studiengang, jedes Modul zu genau einem Semester und jede Prüfungsleistung zu genau einem Modul.
- Die Domain-Klassen speichern dafür Parent-Referenzen. Doppelte oder fremde Zuordnungen werden zurückgewiesen.
- Semesternummern und Modulnamen müssen im Studiengang eindeutig sein. Groß- und Kleinschreibung unterscheiden keine Modulnamen.
- Pro Modul ist höchstens eine Prüfungsleistung je Datum erlaubt, damit die neueste Prüfung eindeutig bleibt.
- Semester und Module benötigen positive ganze Nummern beziehungsweise ECTS-Zahlen. Die Summe der angelegten Modul-ECTS darf die Gesamt-ECTS nicht überschreiten.
- Beim Verschieben bleibt dasselbe Modul mit sämtlichen Prüfungsleistungen erhalten.
- Ein Semester kann erst gelöscht werden, wenn seine Module ausdrücklich gelöscht oder verschoben wurden.
- Ein Studiengang kann erst gelöscht werden, wenn keines seiner Semester Module enthält.
- Beim Löschen eines Moduls werden auch seine Prüfungsleistungen aus dem Datenbestand und den CSV-Dateien entfernt.

## Aufbau des Codes

Die sechs Schichten aus Phase 2 bleiben getrennt:

| Datei | Klassen | Aufgabe |
| --- | --- | --- |
| `domain.py` | `Studiengang`, `Semester`, `Modul`, `Pruefungsleistung` | Fachliche Daten, Zuordnungen und Prüfungen |
| `repository.py` | `StudiengangRepository`, `CsvStudiengangRepository` | Abstrakte Datenschnittstelle und CSV-Speicherung |
| `service.py` | `NotenService` | Berechnung von Noten und erreichten ECTS |
| `controller.py` | `DashboardController` | Menüablauf, Bearbeitung und Vorbereitung der Anzeigewerte |
| `view.py` | `KonsolenView` | Ein- und Ausgabe mit `input()` und `print()` |
| `app.py` | `DashboardApp` | Erzeugt und verbindet Repository, Service, View und Controller |

`main.py` startet die Anwendung.

Die Namen der zehn Anwendungsklassen und aller 27 im UML aus Phase 2 aufgeführten Methoden stimmen mit dem Entwurf überein. Ergänzt wurden Methoden zum Lesen, Bearbeiten und Prüfen der Daten sowie weitere Hilfsmethoden.

Der Code verwendet normale Klassen, Methoden, Schleifen und Listen. `@dataclass` erzeugt die Standardmethoden für die Domain-Objekte. `field(default_factory=list)` gibt jedem Objekt eine eigene Liste. Eigene Attribute und Hilfsmethoden tragen keinen führenden Unterstrich. Andere Schichten greifen auf die Domain-Daten über die `gib_...()`- und Bearbeitungsmethoden zu; Listen werden als Kopien zurückgegeben.

Ein einzelner führender Unterstrich wäre lediglich eine Konvention für interne Namen, kein erzwungener Zugriffsschutz. Die im UML als privat vorgesehenen Daten werden im Programmablauf weiterhin über die dafür vorgesehenen Methoden verwaltet. Python erlaubt aber auch den direkten Zugriff auf die Attribute. Besondere Python-Namen wie `__init__`, `__post_init__` und `__name__` behalten ihre vorgeschriebene Schreibweise. Unterstriche zwischen Wörtern, etwa in `aktuelle_note`, machen mehrteilige Namen lesbar.

Die View erhält nur aufbereitete Zahlen, Texte, Listen und Dictionaries. Sie hält keine Verweise auf Domain-Objekte. Der `NotenService` kennt weder Eingaben noch Dateien. Die abstrakte Repository-Klasse verwendet `ABC` und `@abstractmethod`, sodass die Speicherung später durch eine andere Umsetzung ersetzt werden kann.

## CSV-Dateien

Der Studiengang wird im Ordner `daten/` in vier Dateien gespeichert:

| Datei | Spalten |
| --- | --- |
| `studiengang.csv` | `name;abschluss;ziel_note;ects_gesamt` |
| `semester.csv` | `nummer` |
| `module.csv` | `semester_nummer;name;ects` |
| `pruefungsleistungen.csv` | `modulname;pruefungsdatum;note` |

Die Dateien verwenden UTF-8 und ein Semikolon als Trennzeichen. Das Datum wird als `JJJJ-MM-TT` gespeichert. Beim Laden werden auch UTF-8-Dateien mit BOM sowie Dezimalkommas erkannt.

Änderungen schreiben den gesamten aktuellen Datenbestand neu. Vor dem Ersetzen werden alle neuen Dateien vollständig vorbereitet und die bisherigen Dateien vorübergehend gesichert. Bei einem abgefangenen Schreibfehler wird der vorherige Bestand wiederhergestellt. Der Controller stellt dann auch seinen bisherigen Zustand im Arbeitsspeicher wieder her.

Fehlt beim Laden eine der vier Dateien oder enthält der Bestand widersprüchliche Daten, beendet die Anwendung den Start mit einer Python-Fehlermeldung. Die vorhandenen CSV-Dateien werden dabei nicht überschrieben.

## Hinweise bei Startproblemen

| Problem | Lösung |
| --- | --- |
| `py` wird nicht erkannt | Prüfe die Version mit `python --version` und starte mit `python main.py`, sofern Python 3.10 oder neuer angezeigt wird. |
| Weder `py` noch `python` wird unter Windows erkannt | Prüfe die Python-Installation und öffne anschließend ein neues Terminal. |
| `main.py` wird nicht gefunden | Öffne das Terminal im entpackten Ordner, in dem `main.py` liegt. |
| Ein Anwendungsmodul wird nicht gefunden | Entpacke den vollständigen Programmordner. Alle sieben Python-Dateien müssen im selben Ordner bleiben. |
| Die Daten lassen sich nicht speichern | Verwende einen Programmordner, in dem Du Schreibrechte hast. |

## Vorbereitung für GitHub

Dieser Programmordner kann als Repository verwendet werden. Die `.gitignore` schließt Python-Zwischendateien, virtuelle Umgebungen, lokale Editor-Einstellungen und den Ordner `daten/` mit Deinen persönlichen Studiendaten aus.

Die separate einseitige PDF-Installationsanleitung im Portfolio enthält dieselben fünf Schritte und den GitHub-Link. Diese README ergänzt die Anleitung um Bedienungsbeispiele, Berechnungsregeln und die Beschreibung des Programmaufbaus.
