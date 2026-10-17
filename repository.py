"""Abstrakte Datenschnittstelle und ihre konkrete Umsetzung mit vier CSV-Dateien."""

import csv
import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path

from domain import Modul, Pruefungsleistung, Semester, Studiengang


CSV_SPALTEN = {
    "studiengang.csv": ["name", "abschluss", "ziel_note", "ects_gesamt"],
    "semester.csv": ["nummer"],
    "module.csv": ["semester_nummer", "name", "ects"],
    "pruefungsleistungen.csv": ["modulname", "pruefungsdatum", "note"],
}


class StudiengangRepository(ABC):
    """Legt die gemeinsamen Methoden zum Laden, Speichern und Löschen fest.

    Diese Klasse ist abstrakt. Eine konkrete Unterklasse muss ihre mit
    abstractmethod gekennzeichneten Methoden umsetzen.
    """

    @abstractmethod
    def lade(self) -> Studiengang | None:
        """Lade den gespeicherten Studiengang oder liefere None beim ersten Start."""

    @abstractmethod
    def speichere(self, studiengang: Studiengang) -> None:
        """Speichere den vollständigen aktuellen Datenbestand."""

    @abstractmethod
    def loesche(self) -> None:
        """Lösche einen Studiengang, sofern seine Semester keine Module enthalten."""


class CsvStudiengangRepository(StudiengangRepository):
    """Setzt die Speicherung in vier lokalen CSV-Dateien um und stellt beim Laden die
    Objektbeziehungen wieder her.
    """

    def __init__(self, datenordner: Path) -> None:
        """Merkt sich den übergebenen Datenordner für spätere Dateioperationen.

        Der Ordner wird beim ersten Speichern angelegt.
        """
        self.datenordner = Path(datenordner)

    def lese_datei(self, dateiname: str) -> list[tuple[int, dict[str, str]]]:
        """Liest eine CSV-Datei und prüft ihre Kopfzeile sowie die Anzahl der Spalten.

        Jeder Listeneintrag enthält die Zeilennummer und ein Dictionary mit den
        Spaltenwerten. Ungültige CSV-Daten führen zu einem ValueError.
        """
        dateipfad = self.datenordner / dateiname
        zeilen = []
        # utf-8-sig kann auch CSV-Dateien mit einer UTF-8-BOM aus Excel lesen.
        with dateipfad.open("r", encoding="utf-8-sig", newline="") as datei:
            reader = csv.DictReader(datei, delimiter=";", strict=True)
            try:
                if reader.fieldnames != CSV_SPALTEN[dateiname]:
                    erwartete_spalten = ";".join(CSV_SPALTEN[dateiname])
                    raise ValueError(f"{dateiname}: Erwartete Kopfzeile: {erwartete_spalten}")
                for zeile in reader:
                    if None in zeile or None in zeile.values():
                        raise ValueError(
                            f"{dateiname}, Zeile {reader.line_num}: Falsche Anzahl an Spalten."
                        )
                    zeilen.append((reader.line_num, zeile))
            except csv.Error as fehler:
                raise ValueError(f"{dateiname}: Ungültiges CSV-Format: {fehler}") from fehler
        return zeilen

    def lade(self) -> Studiengang | None:
        """Lädt den Studiengang samt Semestern, Modulen und Prüfungen aus den
        CSV-Dateien.

        Die Zuordnung erfolgt über die prüfenden Domain-Methoden. Ohne vorhandene
        CSV-Dateien wird None zurückgegeben. Unvollständige oder widersprüchliche
        Daten werden zurückgewiesen.
        """
        vorhandene_dateien = []
        fehlende_dateien = []
        for dateiname in CSV_SPALTEN:
            if (self.datenordner / dateiname).exists():
                vorhandene_dateien.append(dateiname)
            else:
                fehlende_dateien.append(dateiname)
        if not vorhandene_dateien:
            return None
        if fehlende_dateien:
            raise ValueError("Unvollständiger Datenbestand. Es fehlen: " + ", ".join(fehlende_dateien))

        studiengang_zeilen = self.lese_datei("studiengang.csv")
        if len(studiengang_zeilen) != 1:
            raise ValueError("studiengang.csv muss genau einen Studiengang enthalten.")
        zeilennummer, zeile = studiengang_zeilen[0]
        try:
            studiengang = Studiengang(
                zeile["name"],
                zeile["abschluss"],
                float(zeile["ziel_note"].replace(",", ".")),
                int(zeile["ects_gesamt"]),
            )
        except ValueError as fehler:
            raise ValueError(f"studiengang.csv, Zeile {zeilennummer}: {fehler}") from fehler

        # Dieselben Domain-Methoden prüfen sowohl Benutzereingaben als auch CSV-Daten.
        for zeilennummer, zeile in self.lese_datei("semester.csv"):
            try:
                semester = Semester(int(zeile["nummer"]))
                studiengang.semester_hinzufuegen(semester)
            except ValueError as fehler:
                raise ValueError(f"semester.csv, Zeile {zeilennummer}: {fehler}") from fehler

        for zeilennummer, zeile in self.lese_datei("module.csv"):
            try:
                semester = studiengang.finde_semester(int(zeile["semester_nummer"]))
                modul = Modul(zeile["name"], int(zeile["ects"]))
                semester.modul_hinzufuegen(modul)
            except ValueError as fehler:
                raise ValueError(f"module.csv, Zeile {zeilennummer}: {fehler}") from fehler

        for zeilennummer, zeile in self.lese_datei("pruefungsleistungen.csv"):
            try:
                modul = studiengang.finde_modul(zeile["modulname"])
                pruefung = Pruefungsleistung(
                    date.fromisoformat(zeile["pruefungsdatum"]),
                    float(zeile["note"].replace(",", ".")),
                )
                modul.pruefungsleistung_hinzufuegen(pruefung)
            except ValueError as fehler:
                raise ValueError(f"pruefungsleistungen.csv, Zeile {zeilennummer}: {fehler}") from fehler
        return studiengang

    def schreibe_datei(self, dateipfad: Path, spalten: list[str], zeilen: list[dict]) -> None:
        """Schreibt eine Kopfzeile und die übergebenen Datensätze als UTF-8-CSV mit
        Semikolon, weil das die in Deutschland typische Formatierung ist.
        """
        with dateipfad.open("w", encoding="utf-8", newline="") as datei:
            writer = csv.DictWriter(datei, fieldnames=spalten, delimiter=";")
            writer.writeheader()
            writer.writerows(zeilen)

    def uebernehme_dateien(self, arbeitsordner: Path, loeschen: bool = False) -> None:
        """Sichert die bisherigen CSV-Dateien und ersetzt oder löscht sie anschließend.

        Mit loeschen=True werden die Dateien entfernt. Andernfalls werden die
        vorbereiteten Dateien aus arbeitsordner übernommen. Bei einem abgefangenen
        Datei- oder Abbruchfehler wird der bisherige Bestand wiederhergestellt.
        """
        sicherungsordner = arbeitsordner / "sicherung"
        sicherungsordner.mkdir()
        # Alle bisherigen Dateien sichern, bevor auch nur eine ersetzt wird.
        for dateiname in CSV_SPALTEN:
            bisherige_datei = self.datenordner / dateiname
            if bisherige_datei.exists():
                shutil.copy2(bisherige_datei, sicherungsordner / dateiname)

        bearbeitete_dateien = []
        try:
            for dateiname in CSV_SPALTEN:
                ziel = self.datenordner / dateiname
                bearbeitete_dateien.append(dateiname)
                if loeschen:
                    if ziel.exists():
                        ziel.unlink()
                else:
                    os.replace(arbeitsordner / dateiname, ziel)
        except (OSError, KeyboardInterrupt):
            # Bei einem Schreibfehler den bisherigen Datenbestand wiederherstellen.
            for dateiname in bearbeitete_dateien:
                sicherung = sicherungsordner / dateiname
                ziel = self.datenordner / dateiname
                if sicherung.exists():
                    os.replace(sicherung, ziel)
                elif ziel.exists():
                    ziel.unlink()
            raise

    def speichere(self, studiengang: Studiengang) -> None:
        """Speichert den vollständigen Studiengang einschließlich aller Zuordnungen.

        Zuerst werden die vier CSV-Dateien in einem temporären Unterordner
        vorbereitet. Anschließend werden die bisherigen Dateien mit Sicherung
        ersetzt.
        """
        studiengang_zeilen = [{
            "name": studiengang.gib_name(),
            "abschluss": studiengang.gib_abschluss(),
            "ziel_note": studiengang.gib_ziel_note(),
            "ects_gesamt": studiengang.gib_ects_gesamt(),
        }]
        semester_zeilen = []
        modul_zeilen = []
        pruefungs_zeilen = []
        for semester in studiengang.gib_semester():
            semester_zeilen.append({"nummer": semester.gib_nummer()})
            for modul in semester.gib_module():
                modul_zeilen.append({
                    "semester_nummer": semester.gib_nummer(),
                    "name": modul.gib_name(),
                    "ects": modul.gib_ects(),
                })
                for pruefung in modul.gib_pruefungsleistungen():
                    pruefungs_zeilen.append({
                        "modulname": modul.gib_name(),
                        "pruefungsdatum": pruefung.gib_pruefungsdatum().isoformat(),
                        "note": pruefung.gib_note(),
                    })
        daten = {
            "studiengang.csv": studiengang_zeilen,
            "semester.csv": semester_zeilen,
            "module.csv": modul_zeilen,
            "pruefungsleistungen.csv": pruefungs_zeilen,
        }

        self.datenordner.mkdir(parents=True, exist_ok=True)
        # Erst vollständig in temporäre Dateien schreiben, dann die CSV-Dateien ersetzen.
        with tempfile.TemporaryDirectory(prefix=".speichern-", dir=self.datenordner) as pfad:
            arbeitsordner = Path(pfad)
            for dateiname, spalten in CSV_SPALTEN.items():
                self.schreibe_datei(arbeitsordner / dateiname, spalten, daten[dateiname])
            self.uebernehme_dateien(arbeitsordner)

    def loesche(self) -> None:
        """Prüft die Löschregeln des Studiengangs und entfernt anschließend seine vier
        CSV-Dateien.

        Falls noch keine Daten vorhanden sind, endet die Methode ohne weitere
        Aktion.
        """
        studiengang = self.lade()
        if studiengang is None:
            return
        studiengang.loesche()
        with tempfile.TemporaryDirectory(prefix=".loeschen-", dir=self.datenordner) as pfad:
            self.uebernehme_dateien(Path(pfad), loeschen=True)
