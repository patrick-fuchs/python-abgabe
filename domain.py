"""Fachliche Objekte und ihre Beziehungen aus dem Entwurf von Phase 2.

eq=False bei den Dataclasses sorgt dafür, dass die Zuordnung das konkrete
Objekt prüft und nicht nur den Inhalt zweier (verschiedener) Objekte vergleicht.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from math import isfinite


def pruefe_text(text: str, bezeichnung: str) -> str:
    """Prüft, ob ein Text leer ist und auf unzulässige Steuerzeichen.

    Gibt den gültigen Text ohne Leerzeichen am Anfang und Ende zurück. Bei einer
    ungültigen Eingabe wird ein ValueError ausgelöst.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{bezeichnung} darf nicht leer sein.")
    if any(zeichen in text for zeichen in ("\n", "\r", "\t", "\x1b")):
        raise ValueError(f"{bezeichnung} darf keine Steuerzeichen enthalten.")
    return text.strip()


def pruefe_positive_ganzzahl(wert: int, bezeichnung: str) -> None:
    """Prüft, ob der Wert eine ganze Zahl größer 0 ist.

    Ungültige Werte, auch True und False, führen zu einem ValueError.
    """
    if type(wert) is not int or wert <= 0:
        raise ValueError(f"{bezeichnung} muss eine positive ganze Zahl sein.")


def pruefe_note(note: float, zielnote: bool = False) -> None:
    """Prüft, ob eine zulässige Note vorliegt.

    Prüfungsnoten dürfen zwischen 1,0 und 4,0 liegen oder 5,0 sein. Wenn zielnote
    True ist, sind nur Werte zwischen 1,0 und 4,0 erlaubt.
    """
    if isinstance(note, bool) or not isinstance(note, (int, float)):
        raise ValueError("Eine Note muss eine Zahl sein.")
    if not isfinite(note):
        raise ValueError("Eine Note muss eine endliche Zahl sein.")
    if 1.0 <= note <= 4.0:
        return
    if not zielnote and note == 5.0:
        return
    if zielnote:
        raise ValueError("Die Zielnote muss zwischen 1,0 und 4,0 liegen.")
    raise ValueError("Die Note muss zwischen 1,0 und 4,0 liegen oder 5,0 sein.")


@dataclass(eq=False)
class Pruefungsleistung:
    """Speichert Datum und Note einer Prüfung sowie ihre Zuordnung zu einem Modul."""

    pruefungsdatum: date
    note: float
    modul: Modul | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Prüft Datum und Note automatisch nach dem Erzeugen durch die Dataclass."""
        self.bearbeite(self.pruefungsdatum, self.note)

    def gib_pruefungsdatum(self) -> date:
        """Gibt das Datum der Prüfungsleistung zurück."""
        return self.pruefungsdatum

    def gib_note(self) -> float:
        """Gibt die Note der Prüfungsleistung zurück."""
        return self.note

    def gib_modul(self) -> Modul | None:
        """Gibt das zugeordnete Modul zurück oder None, wenn keine Zuordnung besteht."""
        return self.modul

    def bearbeite(self, pruefungsdatum: date, note: float) -> None:
        """Prüft ein neues Datum und eine neue Note und übernimmt anschließend die
        Werte.

        Bei einer zugeordneten Prüfung wird auch geprüft, ob ihr Modul schon eine
        andere Prüfung am neuen Datum enthält.
        """
        if type(pruefungsdatum) is not date:
            raise ValueError("Das Prüfungsdatum muss ein gültiges Datum sein.")
        pruefe_note(note)
        if self.modul is not None:
            self.modul.pruefe_pruefungsdatum(pruefungsdatum, ausnahme=self)
        self.pruefungsdatum = pruefungsdatum
        self.note = float(note)


@dataclass(eq=False)
class Modul:
    """Verwaltet Modulname, ECTS-Punkte, Prüfungsleistungen und die Semesterzuordnung."""

    name: str
    ects: int
    pruefungsleistungen: list[Pruefungsleistung] = field(
        default_factory=list, init=False, repr=False
    )
    semester: Semester | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Prüft Name und ECTS-Punkte automatisch nach dem Erzeugen durch die Dataclass."""
        self.bearbeite(self.name, self.ects)

    def gib_name(self) -> str:
        """Gibt den Namen des Moduls zurück."""
        return self.name

    def gib_ects(self) -> int:
        """Gibt die ECTS-Punkte des Moduls zurück."""
        return self.ects

    def gib_semester(self) -> Semester | None:
        """Gibt das zugeordnete Semester zurück oder None, wenn keine Zuordnung besteht."""
        return self.semester

    def gib_pruefungsleistungen(self) -> list[Pruefungsleistung]:
        """Gibt eine Kopie der Prüfungsliste zurück.

        Die enthaltenen Prüfungsobjekte bleiben dieselben. Änderungen an der
        zurückgegebenen Liste verändern die interne Liste nicht.
        """
        # Eine Kopie verhindert, dass andere Schichten die interne Liste ändern.
        return self.pruefungsleistungen.copy()

    def bearbeite(self, name: str, ects: int) -> None:
        """Prüft und ändert den Namen und die ECTS-Punkte des Moduls.

        Bei einem zugeordneten Modul werden auch eindeutige Namen und die
        ECTS-Grenze des Studiengangs geprüft.
        """
        name = pruefe_text(name, "Der Modulname")
        pruefe_positive_ganzzahl(ects, "Die ECTS-Zahl")
        if self.semester is not None:
            studiengang = self.semester.gib_studiengang()
            if studiengang is not None:
                studiengang.pruefe_modul(name, ects, ausnahme=self)
        self.name = name
        self.ects = ects

    def pruefe_pruefungsdatum(
        self, pruefungsdatum: date, ausnahme: Pruefungsleistung | None = None
    ) -> None:
        """Prüft, ob das Datum noch für eine Prüfungsleistung verfügbar ist.

        Die mit ausnahme übergebene Prüfung wird ausgelassen, damit sie ihr eigenes
        Datum beim Bearbeiten behalten darf.
        """
        # Zwei Versuche am selben Tag hätten kein eindeutig neuestes Datum.
        for pruefung in self.pruefungsleistungen:
            if pruefung is not ausnahme:
                if pruefung.gib_pruefungsdatum() == pruefungsdatum:
                    raise ValueError("Für dieses Modul gibt es an diesem Tag schon eine Prüfung.")

    def pruefungsleistung_hinzufuegen(self, pruefungsleistung: Pruefungsleistung) -> None:
        """Ordnet eine Prüfungsleistung diesem Modul zu und speichert die
        Modulreferenz.

        Das Modul muss bereits einem Semester angehören. Doppelte oder fremde
        Zuordnungen und mehrfach vergebene Prüfungsdaten werden zurückgewiesen.
        """
        if self.semester is None:
            raise ValueError("Das Modul muss zuerst einem Semester zugeordnet werden.")
        if pruefungsleistung in self.pruefungsleistungen:
            raise ValueError("Diese Prüfungsleistung ist bereits im Modul enthalten.")
        if pruefungsleistung.gib_modul() is not None:
            raise ValueError("Diese Prüfungsleistung gehört bereits zu einem anderen Modul.")
        self.pruefe_pruefungsdatum(pruefungsleistung.gib_pruefungsdatum())
        self.pruefungsleistungen.append(pruefungsleistung)
        pruefungsleistung.modul = self

    def pruefungsleistung_loeschen(self, pruefungsleistung: Pruefungsleistung) -> None:
        """Entfernt eine zugehörige Prüfungsleistung und löst ihre Zuordnung zum Modul."""
        if pruefungsleistung not in self.pruefungsleistungen:
            raise ValueError("Diese Prüfungsleistung gehört nicht zu diesem Modul.")
        self.pruefungsleistungen.remove(pruefungsleistung)
        pruefungsleistung.modul = None

    def aktuelle_pruefungsleistung(self) -> Pruefungsleistung | None:
        """Gibt die Prüfung mit dem neuesten Datum zurück oder None, wenn keine Prüfung
        vorliegt.
        """
        neueste_pruefung = None
        for pruefung in self.pruefungsleistungen:
            if neueste_pruefung is None:
                neueste_pruefung = pruefung
            elif pruefung.gib_pruefungsdatum() > neueste_pruefung.gib_pruefungsdatum():
                neueste_pruefung = pruefung
        return neueste_pruefung

    def aktuelle_note(self) -> float | None:
        """Gibt die Note der neuesten Prüfung zurück oder None, wenn keine Prüfung
        vorliegt. Auch eine nicht bestandene Prüfung mit der Note 5,0 kann die neueste
        Prüfung sein.
        """
        pruefung = self.aktuelle_pruefungsleistung()
        if pruefung is None:
            return None
        return pruefung.gib_note()


@dataclass(eq=False)
class Semester:
    """Verwaltet die Semesternummer, die zugehörigen Module und die Studiengangszuordnung."""

    nummer: int
    module: list[Modul] = field(default_factory=list, init=False, repr=False)
    studiengang: Studiengang | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Prüft die Semesternummer automatisch nach dem Erzeugen durch die Dataclass."""
        self.bearbeite(self.nummer)

    def gib_nummer(self) -> int:
        """Gibt die Nummer des Semesters zurück."""
        return self.nummer

    def gib_studiengang(self) -> Studiengang | None:
        """Gibt den zugeordneten Studiengang zurück oder None, wenn keine Zuordnung besteht."""
        return self.studiengang

    def gib_module(self) -> list[Modul]:
        """Gibt eine Kopie der Modulliste zurück.

        Die enthaltenen Modulobjekte bleiben dieselben. Änderungen an der
        zurückgegebenen Liste verändern die interne Liste nicht.
        """
        return self.module.copy()

    def bearbeite(self, nummer: int) -> None:
        """Prüft und ändert die Semesternummer.

        Die Nummer muss positiv und innerhalb des zugeordneten Studiengangs
        eindeutig sein.
        """
        pruefe_positive_ganzzahl(nummer, "Die Semesternummer")
        if self.studiengang is not None:
            for semester in self.studiengang.gib_semester():
                if semester is not self and semester.gib_nummer() == nummer:
                    raise ValueError("Diese Semesternummer ist bereits vergeben.")
        self.nummer = nummer

    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Ordnet ein Modul diesem Semester zu und speichert seine Semesterreferenz.

        Das Semester muss bereits einem Studiengang gehören. Die Zuordnung sowie
        Modulname und ECTS-Punkte werden vor dem Hinzufügen geprüft.
        """
        if self.studiengang is None:
            raise ValueError("Das Semester muss zuerst einem Studiengang zugeordnet werden.")
        if modul in self.module:
            raise ValueError("Dieses Modul ist bereits im Semester enthalten.")
        if modul.gib_semester() is not None:
            raise ValueError("Dieses Modul gehört bereits zu einem anderen Semester.")
        self.studiengang.pruefe_modul(modul.gib_name(), modul.gib_ects())
        self.module.append(modul)
        modul.semester = self

    def modul_loeschen(self, modul: Modul) -> None:
        """Entfernt ein zugehöriges Modul einschließlich seiner Prüfungsleistungen.

        Dabei werden die Zuordnungen der Prüfungen und des Moduls gelöst. Die
        nächste Speicherung übernimmt den verbleibenden Bestand in die CSV-Dateien.
        """
        if modul not in self.module:
            raise ValueError("Dieses Modul gehört nicht zu diesem Semester.")
        # Komposition: Beim Löschen verschwinden auch alle Prüfungsleistungen.
        for pruefung in modul.gib_pruefungsleistungen():
            modul.pruefungsleistung_loeschen(pruefung)
        self.module.remove(modul)
        modul.semester = None


@dataclass(eq=False)
class Studiengang:
    """Verwaltet die Stammdaten des Studiengangs, seine Semester und die Zuordnungsregeln."""

    name: str
    abschluss: str
    ziel_note: float
    ects_gesamt: int
    semester: list[Semester] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Prüft die Stammdaten automatisch nach dem Erzeugen durch die Dataclass."""
        self.bearbeite(self.name, self.abschluss, self.ziel_note, self.ects_gesamt)

    def gib_name(self) -> str:
        """Gibt den Namen des Studiengangs zurück."""
        return self.name

    def gib_abschluss(self) -> str:
        """Gibt die Bezeichnung des angestrebten Abschlusses zurück."""
        return self.abschluss

    def gib_ziel_note(self) -> float:
        """Gibt die festgelegte Zielnote zurück."""
        return self.ziel_note

    def gib_ects_gesamt(self) -> int:
        """Gibt die für den gesamten Studiengang vorgesehenen ECTS-Punkte zurück."""
        return self.ects_gesamt

    def gib_semester(self) -> list[Semester]:
        """Gibt eine Kopie der Semesterliste zurück.

        Die enthaltenen Semesterobjekte bleiben dieselben. Änderungen an der
        zurückgegebenen Liste verändern die interne Liste nicht.
        """
        return self.semester.copy()

    def gib_alle_module(self) -> list[Modul]:
        """Stellt alle Module der zugeordneten Semester in einer neuen Liste zusammen."""
        module = []
        for semester in self.semester:
            module.extend(semester.gib_module())
        return module

    def gib_geplante_ects(self) -> int:
        """Summiert die ECTS-Punkte aller angelegten Module, unabhängig von ihren
        Prüfungsnoten.
        """
        ects = 0
        for modul in self.gib_alle_module():
            ects += modul.gib_ects()
        return ects

    def bearbeite(self, name: str, abschluss: str, ziel_note: float, ects_gesamt: int) -> None:
        """Prüft und ändert Name, Abschluss, Zielnote und Gesamt-ECTS.

        Die Gesamt-ECTS dürfen nicht kleiner als die Summe der bereits angelegten
        Modul-ECTS sein.
        """
        name = pruefe_text(name, "Der Studiengangname")
        abschluss = pruefe_text(abschluss, "Der Abschluss")
        pruefe_note(ziel_note, zielnote=True)
        pruefe_positive_ganzzahl(ects_gesamt, "Die Gesamtzahl der ECTS-Punkte")
        if ects_gesamt < self.gib_geplante_ects():
            raise ValueError("Die Gesamt-ECTS dürfen nicht kleiner als die Summe der Modul-ECTS sein.")
        self.name = name
        self.abschluss = abschluss
        self.ziel_note = float(ziel_note)
        self.ects_gesamt = ects_gesamt

    def semester_hinzufuegen(self, semester: Semester) -> None:
        """Ordnet ein Semester diesem Studiengang zu und speichert seine
        Studiengangsreferenz.

        Bereits zugeordnete Semester und doppelte Semesternummern werden
        zurückgewiesen.
        """
        if semester in self.semester:
            raise ValueError("Dieses Semester ist bereits im Studiengang enthalten.")
        if semester.gib_studiengang() is not None:
            raise ValueError("Dieses Semester gehört bereits zu einem anderen Studiengang.")
        for vorhandenes_semester in self.semester:
            if vorhandenes_semester.gib_nummer() == semester.gib_nummer():
                raise ValueError("Diese Semesternummer ist bereits vergeben.")
        self.semester.append(semester)
        semester.studiengang = self

    def semester_loeschen(self, semester: Semester) -> None:
        """Entfernt ein zugehöriges Semester, sofern es keine Module mehr enthält.

        Anschließend wird die Studiengangsreferenz des Semesters gelöst.
        """
        if semester not in self.semester:
            raise ValueError("Dieses Semester gehört nicht zu diesem Studiengang.")
        if semester.gib_module():
            raise ValueError("Lösche oder verschiebe zuerst die Module dieses Semesters.")
        self.semester.remove(semester)
        semester.studiengang = None

    def finde_semester(self, nummer: int) -> Semester:
        """Gibt das Semester mit der gesuchten Nummer zurück oder löst einen ValueError aus."""
        for semester in self.semester:
            if semester.gib_nummer() == nummer:
                return semester
        raise ValueError(f"Das Semester {nummer} existiert nicht.")

    def finde_modul(self, name: str) -> Modul:
        """Gibt das Modul mit dem gesuchten Namen zurück oder löst einen ValueError
        aus.

        Groß- und Kleinschreibung spielen beim Vergleich keine Rolle. Leerzeichen am
        Anfang und Ende des gesuchten Namens werden entfernt.
        """
        for modul in self.gib_alle_module():
            if modul.gib_name().casefold() == name.strip().casefold():
                return modul
        raise ValueError(f"Das Modul '{name}' existiert nicht.")

    def pruefe_modul(self, name: str, ects: int, ausnahme: Modul | None = None) -> None:
        """Prüft die Eindeutigkeit eines Modulnamens sowie die gesamte geplante
        ECTS-Zahl.

        Das mit ausnahme übergebene Modul wird ausgelassen, damit beim Bearbeiten
        seine neuen Werte anstelle der bisherigen Werte zählen.
        """
        ects_summe = ects
        for modul in self.gib_alle_module():
            if modul is ausnahme:
                continue
            if modul.gib_name().casefold() == name.casefold():
                raise ValueError("Der Modulname ist im Studiengang bereits vergeben.")
            ects_summe += modul.gib_ects()
        if ects_summe > self.ects_gesamt:
            raise ValueError("Die Summe der Modul-ECTS überschreitet die Gesamt-ECTS des Studiengangs.")

    def verschiebe_modul(self, modulname: str, zielsemester_nummer: int) -> None:
        """Verschiebt dasselbe Modul in ein anderes Semester dieses Studiengangs.

        Prüfungsleistungen bleiben erhalten. Die bisherigen Zuordnungen und das
        Zielsemester werden geprüft, anschließend wird die Semesterreferenz
        aktualisiert.
        """
        modul = self.finde_modul(modulname)
        bisheriges_semester = modul.gib_semester()
        zielsemester = self.finde_semester(zielsemester_nummer)
        if bisheriges_semester is None or modul not in bisheriges_semester.gib_module():
            raise ValueError("Das Modul ist seinem bisherigen Semester nicht korrekt zugeordnet.")
        if bisheriges_semester.gib_studiengang() is not self:
            raise ValueError("Das bisherige Semester gehört nicht zu diesem Studiengang.")
        if bisheriges_semester is zielsemester:
            raise ValueError("Das Modul ist bereits im Zielsemester.")
        # Hier wird dasselbe Objekt verschoben. Seine Prüfungen bleiben erhalten.
        bisheriges_semester.module.remove(modul)
        zielsemester.module.append(modul)
        modul.semester = zielsemester

    def loesche(self) -> None:
        """Entfernt alle Semester zur Vorbereitung der Studiengangslöschung.

        Die Löschung ist nur erlaubt, wenn keines der Semester mehr Module enthält.
        """
        for semester in self.semester:
            if semester.gib_module():
                raise ValueError("Lösche zuerst alle Module, bevor Du den Studiengang löschst.")
        for semester in self.gib_semester():
            self.semester_loeschen(semester)
