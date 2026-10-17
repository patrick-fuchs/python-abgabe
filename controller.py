"""Programmablauf, Bearbeitung der Daten und Vorbereitung des Dashboards."""

from copy import deepcopy
from datetime import date, datetime
from math import isclose

from domain import Modul, Pruefungsleistung, Semester, Studiengang
from repository import StudiengangRepository
from service import NotenService
from view import KonsolenView, formatiere_note


def semesternummer(semester: Semester) -> int:
    """Gibt die Semesternummer als Vergleichswert für die Sortierung zurück."""
    return semester.gib_nummer()


def modulname(modul: Modul) -> str:
    """Gibt den Modulnamen als Vergleichswert ohne Unterscheidung der Groß- und
    Kleinschreibung zurück.
    """
    return modul.gib_name().casefold()


def pruefungsdatum(pruefung: Pruefungsleistung) -> date:
    """Gibt das Prüfungsdatum als Vergleichswert für die Sortierung zurück."""
    return pruefung.gib_pruefungsdatum()


def letztes_pruefungsdatum(modul: Modul) -> date:
    """Gibt das Datum der neuesten Prüfung eines Moduls zurück.

    Ohne Prüfung wird date.min verwendet, das früheste mit date darstellbare Datum.
    """
    pruefung = modul.aktuelle_pruefungsleistung()
    if pruefung is None:
        return date.min
    return pruefung.gib_pruefungsdatum()


def liegt_im_ziel(note: float, ziel_note: float) -> bool:
    """Liefert True, wenn die Note höchstens so groß wie die Zielnote ist.

    Sehr kleine Rundungsabweichungen von Kommazahlen werden beim Vergleich
    berücksichtigt.
    """
    # Kleine Rundungsabweichungen von float sollen die Zielaussage nicht verändern.
    return note <= ziel_note or isclose(note, ziel_note, abs_tol=1e-9)


class DashboardController:
    """Steuert die Menüaktionen und bereitet die Daten für die Anzeige vor."""

    def __init__(
        self, repository: StudiengangRepository, service: NotenService, view: KonsolenView
    ) -> None:
        """Speichert die übergebenen Objekte für Speicherung, Berechnung und Anzeige.

        self.studiengang hält später den geladenen oder neu angelegten Studiengang.
        Am Anfang steht dort None.
        """
        self.repository = repository
        self.service = service
        self.view = view
        self.studiengang: Studiengang | None = None

    def start(self) -> None:
        """Lädt die gespeicherten Daten und verarbeitet die Menüauswahl bis zum
        Beenden.

        Erfolgreiche Änderungen werden gespeichert. Bei einem abgefangenen Eingabe-
        oder Speicherfehler wird der vorherige Studiengang wieder eingesetzt.
        """
        self.studiengang = self.repository.lade()
        self.view.zeige_dashboard(self.lade_dashboard_daten())

        while True:
            auswahl = self.view.zeige_menu()
            if auswahl == "0":
                self.view.zeige_meldung("Programm beendet. Deine gespeicherten Daten bleiben erhalten.")
                return
            if auswahl == "1":
                self.view.zeige_dashboard(self.lade_dashboard_daten())
                continue
            if auswahl not in ("2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"):
                self.view.zeige_fehler("Wähle einen Menüpunkt von 0 bis 14.")
                continue

            # Eine vollständige Kopie hält die Parent-Referenzen zusammen.
            sicherung = deepcopy(self.studiengang)
            try:
                geaendert = self.bearbeite_daten(auswahl)
                if not geaendert:
                    self.view.zeige_meldung("Aktion abgebrochen.")
                    continue
                if self.studiengang is None:
                    self.repository.loesche()
                else:
                    self.repository.speichere(self.studiengang)
            except ValueError as fehler:
                self.studiengang = sicherung
                self.view.zeige_fehler(str(fehler))
            except OSError as fehler:
                self.studiengang = sicherung
                self.view.zeige_fehler(f"Die Änderung konnte nicht gespeichert werden: {fehler}")
            else:
                self.view.zeige_meldung("Änderung gespeichert.")
                self.view.zeige_dashboard(self.lade_dashboard_daten())

    def lade_dashboard_daten(self) -> dict:
        """Stellt die Kennzahlen und sortierten Module für das Dashboard zusammen.

        Die View erhält Zahlen und Texte in Listen und Dictionaries. Ohne
        Studiengang wird ein leeres Dictionary zurückgegeben.
        """
        if self.studiengang is None:
            return {}
        studiengang = self.studiengang
        aktueller_schnitt = self.service.berechne_aktuellen_schnitt(studiengang)
        best_case = self.service.berechne_best_case(studiengang)
        worst_case = self.service.berechne_worst_case(studiengang)
        erreichte_ects = self.service.berechne_erreichte_ects(studiengang)
        ziel_note = studiengang.gib_ziel_note()

        # Für die Angabe über den Zielnotendurchschnitt
        if aktueller_schnitt is None:
            ziel_status = "Noch keine bestandene Prüfungsleistung vorhanden."
        elif erreichte_ects == studiengang.gib_ects_gesamt():
            if liegt_im_ziel(aktueller_schnitt, ziel_note):
                ziel_status = "Studium abgeschlossen: Zielnote erreicht."
            else:
                ziel_status = "Studium abgeschlossen: Zielnote verfehlt."
        elif best_case is not None and not liegt_im_ziel(best_case, ziel_note):
            ziel_status = "Die Zielnote ist mit den bisherigen Noten rechnerisch nicht mehr erreichbar."
        elif liegt_im_ziel(aktueller_schnitt, ziel_note):
            ziel_status = "Der aktuelle Schnitt liegt im Zielbereich."
        else:
            ziel_status = "Der aktuelle Schnitt liegt über der Zielnote. Das Ziel ist noch erreichbar."

        # Semesterdaten inklusive Sortierung
        # reverse=True für absteigende Formatierung wie gewünscht in Phasen 1 + 2
        semester_daten = []
        semester_liste = sorted(studiengang.gib_semester(), key=semesternummer, reverse=True)
        for semester in semester_liste:
            mit_pruefung = []
            ohne_pruefung = []
            for modul in semester.gib_module():
                if modul.aktuelle_pruefungsleistung() is None:
                    ohne_pruefung.append(modul)
                else:
                    mit_pruefung.append(modul)
            # Zuerst nach Namen sortieren: Bei gleichem Prüfungsdatum bleibt die
            # alphabetische Reihenfolge durch die stabile Python-Sortierung erhalten.
            mit_pruefung.sort(key=modulname)
            mit_pruefung.sort(key=letztes_pruefungsdatum, reverse=True)
            ohne_pruefung.sort(key=modulname)
            modul_daten = []
            for modul in mit_pruefung + ohne_pruefung:
                modul_daten.append({"name": modul.gib_name(), "note": modul.aktuelle_note()})
            semester_daten.append({"nummer": semester.gib_nummer(), "module": modul_daten})

        # Die View erhält ausschließlich die "fertigen" Werte
        return {
            "name": studiengang.gib_name(),
            "abschluss": studiengang.gib_abschluss(),
            "ziel_note": ziel_note,
            "aktueller_schnitt": aktueller_schnitt,
            "best_case": best_case,
            "worst_case": worst_case,
            "ects_erreicht": erreichte_ects,
            "ects_gesamt": studiengang.gib_ects_gesamt(),
            "fortschritt": erreichte_ects / studiengang.gib_ects_gesamt() * 100,
            "ziel_status": ziel_status,
            "semester": semester_daten,
        }

    def lese_text(self, bezeichnung: str, standard: str | None = None) -> str:
        """Liest einen Text und übernimmt bei leerer Eingabe den Vorgabewert standard.

        Ohne Vorgabewert führt eine leere Eingabe zu einem ValueError mit einer
        Fehlermeldung.
        """
        if standard is None:
            text = self.view.lese_eingabe(f"{bezeichnung}: ")
        else:
            text = self.view.lese_eingabe(f"{bezeichnung} [{standard}]: ")
            if not text:
                return standard
        if not text:
            raise ValueError(f"{bezeichnung} darf nicht leer sein.")
        return text

    def lese_ganzzahl(self, bezeichnung: str, standard: int | None = None) -> int:
        """Liest eine Eingabe und gibt sie als ganze Zahl zurück.

        Bei einer leeren Eingabe gilt der vorhandene Vorgabewert. Nicht umwandelbare
        Eingaben führen zu einem ValueError.
        """
        standardtext = None if standard is None else str(standard)
        text = self.lese_text(bezeichnung, standardtext)
        try:
            return int(text)
        except ValueError as fehler:
            raise ValueError(f"{bezeichnung}: Bitte gib eine ganze Zahl ein.") from fehler

    def lese_note(self, bezeichnung: str, standard: float | None = None) -> float:
        """Liest eine Note mit Dezimalkomma oder Dezimalpunkt und gibt eine Kommazahl
        zurück.

        Bei leerer Eingabe bleibt ein vorhandener Vorgabewert ungerundet erhalten.
        """
        # Der Vorgabewert bleibt ungerundet, damit Enter die gespeicherte Note erhält.
        standardtext = None if standard is None else str(standard).replace(".", ",")
        text = self.lese_text(bezeichnung, standardtext)
        try:
            return float(text.replace(",", "."))
        except ValueError as fehler:
            raise ValueError(f"{bezeichnung}: Bitte gib eine Zahl ein, zum Beispiel 2,3.") from fehler

    def lese_datum(self, standard: date | None = None) -> date:
        """Liest ein Datum im Format TT.MM.JJJJ oder JJJJ-MM-TT und gibt ein
        date-Objekt zurück.

        Bei leerer Eingabe wird ein vorhandenes Datum übernommen. Ungültige Eingaben
        führen zu einem ValueError.
        """
        standardtext = None if standard is None else standard.strftime("%d.%m.%Y")
        text = self.lese_text("Prüfungsdatum (TT.MM.JJJJ oder JJJJ-MM-TT)", standardtext)
        try:
            return datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            try:
                return date.fromisoformat(text)
            except ValueError as fehler:
                raise ValueError("Ungültiges Datum. Beispiel: 12.10.2026 oder 2026-10-12.") from fehler

    def brauche_studiengang(self) -> Studiengang:
        """Gibt den aktuellen Studiengang zurück oder meldet mit ValueError, dass
        zuerst einer angelegt werden muss.
        """
        if self.studiengang is None:
            raise ValueError("Lege zuerst über Menüpunkt 2 einen Studiengang an.")
        return self.studiengang

    def lese_auswahl(self, anzahl: int) -> int:
        """Liest eine Auswahlnummer von 1 bis anzahl und gibt den zugehörigen
        Listenindex zurück.

        Listen beginnen bei 0: Aus der eingegebenen Nummer 1 wird deshalb der Index
        0. Nicht vorhandene Nummern führen zu einem ValueError.
        """
        nummer = self.lese_ganzzahl("Deine Auswahl")
        if nummer < 1 or nummer > anzahl:
            raise ValueError("Diese Auswahl ist nicht vorhanden.")
        return nummer - 1

    def waehle_semester(self, titel: str = "Semester auswählen") -> Semester:
        """Zeigt die Semester nach Nummern sortiert an und gibt das ausgewählte
        Semester-Objekt zurück.
        """
        semester_liste = sorted(self.brauche_studiengang().gib_semester(), key=semesternummer)
        if not semester_liste:
            raise ValueError("Lege zuerst ein Semester an.")
        eintraege = []
        for semester in semester_liste:
            eintraege.append(f"Semester {semester.gib_nummer()}")
        self.view.zeige_auswahl(titel, eintraege)
        return semester_liste[self.lese_auswahl(len(semester_liste))]

    def waehle_modul(self) -> Modul:
        """Zeigt die Module alphabetisch an und gibt das ausgewählte Modul-Objekt zurück."""
        module = sorted(self.brauche_studiengang().gib_alle_module(), key=modulname)
        if not module:
            raise ValueError("Lege zuerst ein Modul an.")
        eintraege = []
        for modul in module:
            semester = modul.gib_semester()
            eintraege.append(f"{modul.gib_name()} (Semester {semester.gib_nummer()})")
        self.view.zeige_auswahl("Modul auswählen", eintraege)
        return module[self.lese_auswahl(len(module))]

    def waehle_pruefung(self, modul: Modul) -> Pruefungsleistung:
        """Zeigt die Prüfungen eines Moduls mit der neuesten zuerst an und gibt die
        ausgewählte Prüfung zurück.
        """
        pruefungen = sorted(modul.gib_pruefungsleistungen(), key=pruefungsdatum, reverse=True)
        if not pruefungen:
            raise ValueError("Für dieses Modul gibt es noch keine Prüfungsleistung.")
        eintraege = []
        for pruefung in pruefungen:
            datum = pruefung.gib_pruefungsdatum().strftime("%d.%m.%Y")
            eintraege.append(f"{datum}: Note {formatiere_note(pruefung.gib_note())}")
        self.view.zeige_auswahl("Prüfungsleistung auswählen", eintraege)
        return pruefungen[self.lese_auswahl(len(pruefungen))]

    def bearbeite_daten(self, auswahl: str) -> bool:
        """Führt die zur Menünummer gehörende Bearbeitung aus.

        True kennzeichnet eine erfolgreiche Änderung. False bedeutet, dass eine
        Löschung nicht bestätigt wurde. Das Speichern übernimmt anschließend die
        Methode start.
        """
        if auswahl == "2":
            self.studiengang_anlegen()
        elif auswahl == "3":
            self.studiengang_bearbeiten()
        elif auswahl == "4":
            return self.studiengang_loeschen()
        elif auswahl == "5":
            studiengang = self.brauche_studiengang()
            nummer = self.lese_ganzzahl("Neue Semesternummer")
            studiengang.semester_hinzufuegen(Semester(nummer))
        elif auswahl == "6":
            semester = self.waehle_semester()
            nummer = self.lese_ganzzahl("Neue Semesternummer", semester.gib_nummer())
            semester.bearbeite(nummer)
        elif auswahl == "7":
            return self.semester_loeschen()
        elif auswahl == "8":
            semester = self.waehle_semester()
            name = self.lese_text("Modulname")
            ects = self.lese_ganzzahl("ECTS-Punkte")
            semester.modul_hinzufuegen(Modul(name, ects))
        elif auswahl == "9":
            modul = self.waehle_modul()
            name = self.lese_text("Modulname", modul.gib_name())
            ects = self.lese_ganzzahl("ECTS-Punkte", modul.gib_ects())
            modul.bearbeite(name, ects)
        elif auswahl == "10":
            modul = self.waehle_modul()
            zielsemester = self.waehle_semester("Zielsemester auswählen")
            self.brauche_studiengang().verschiebe_modul(modul.gib_name(), zielsemester.gib_nummer())
        elif auswahl == "11":
            return self.modul_loeschen()
        elif auswahl == "12":
            modul = self.waehle_modul()
            datum = self.lese_datum()
            note = self.lese_note("Note (1,0 bis 4,0 oder 5,0 für nicht bestanden)")
            modul.pruefungsleistung_hinzufuegen(Pruefungsleistung(datum, note))
        elif auswahl == "13":
            modul = self.waehle_modul()
            pruefung = self.waehle_pruefung(modul)
            datum = self.lese_datum(pruefung.gib_pruefungsdatum())
            note = self.lese_note("Note", pruefung.gib_note())
            pruefung.bearbeite(datum, note)
        elif auswahl == "14":
            return self.pruefung_loeschen()
        return True

    def studiengang_anlegen(self) -> None:
        """Fragt die Stammdaten ab und legt den Studiengang an.

        Ein bereits vorhandener Studiengang wird durch diese Aktion nicht
        überschrieben.
        """
        if self.studiengang is not None:
            raise ValueError("Es gibt bereits einen Studiengang. Bearbeite ihn über Menüpunkt 3.")
        name = self.lese_text("Studiengangname")
        abschluss = self.lese_text("Abschluss, zum Beispiel B.Sc.")
        ziel_note = self.lese_note("Zielnote", 2.3)
        ects = self.lese_ganzzahl("Gesamt-ECTS", 180)
        self.studiengang = Studiengang(name, abschluss, ziel_note, ects)

    def studiengang_bearbeiten(self) -> None:
        """Fragt neue Stammdaten ab und ändert den vorhandenen Studiengang.

        Enter übernimmt jeweils den bisherigen Wert.
        """
        studiengang = self.brauche_studiengang()
        self.view.zeige_meldung("Enter übernimmt den bisherigen Wert.")
        name = self.lese_text("Studiengangname", studiengang.gib_name())
        abschluss = self.lese_text("Abschluss", studiengang.gib_abschluss())
        ziel_note = self.lese_note("Zielnote", studiengang.gib_ziel_note())
        ects = self.lese_ganzzahl("Gesamt-ECTS", studiengang.gib_ects_gesamt())
        studiengang.bearbeite(name, abschluss, ziel_note, ects)

    def semester_loeschen(self) -> bool:
        """Löscht ein ausgewähltes leeres Semester nach Bestätigung.

        Gibt True nach der Löschung und False bei abgelehnter Bestätigung zurück.
        """
        semester = self.waehle_semester()
        if semester.gib_module():
            raise ValueError("Lösche oder verschiebe zuerst die Module dieses Semesters.")
        if not self.view.bestaetige(f"Semester {semester.gib_nummer()} wirklich löschen?"):
            return False
        self.brauche_studiengang().semester_loeschen(semester)
        return True

    def modul_loeschen(self) -> bool:
        """Löscht ein ausgewähltes Modul mitsamt seiner Prüfungen nach Bestätigung.

        Gibt True nach der Löschung und False bei abgelehnter Bestätigung zurück.
        """
        modul = self.waehle_modul()
        text = f"Modul '{modul.gib_name()}' einschließlich aller Prüfungsleistungen wirklich löschen?"
        if not self.view.bestaetige(text):
            return False
        modul.gib_semester().modul_loeschen(modul)
        return True

    def pruefung_loeschen(self) -> bool:
        """Löscht eine ausgewählte Prüfungsleistung nach Bestätigung.

        Gibt True nach der Löschung und False bei abgelehnter Bestätigung zurück.
        """
        modul = self.waehle_modul()
        pruefung = self.waehle_pruefung(modul)
        if not self.view.bestaetige("Diese Prüfungsleistung wirklich löschen?"):
            return False
        modul.pruefungsleistung_loeschen(pruefung)
        return True

    def studiengang_loeschen(self) -> bool:
        """Entfernt den Studiengang nach Bestätigung, sofern keine Module mehr
        zugeordnet sind.

        Gibt True nach der Löschung und False bei abgelehnter Bestätigung zurück.
        None kennzeichnet anschließend den fehlenden Studiengang.
        """
        studiengang = self.brauche_studiengang()
        if studiengang.gib_alle_module():
            raise ValueError("Lösche zuerst alle Module, bevor Du den Studiengang löschst.")
        if not self.view.bestaetige("Den Studiengang mit seinen leeren Semestern wirklich löschen?"):
            return False
        studiengang.loesche()
        self.studiengang = None
        return True
