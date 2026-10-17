"""Deutsche Ein- und Ausgabe der Konsolenanwendung."""

from textwrap import wrap


def formatiere_note(note: float | None, nachkommastellen: int = 2) -> str:
    """Formatiert eine Note mit Dezimalkomma und der gewünschten Anzahl an
    Nachkommastellen.

    Für None wird die Zeichenfolge -- zurückgegeben.
    """
    if note is None:
        return "--"
    return f"{note:.{nachkommastellen}f}".replace(".", ",")


class KonsolenView:
    """Übernimmt die deutschsprachige Ein- und Ausgabe im Terminal."""

    def zeige_menu(self) -> str:
        """Zeigt die verfügbaren Menüaktionen und gibt die eingegebene Menünummer als
        Text zurück.
        """
        print("\nWas möchtest Du tun?")
        print("-" * 78)
        menuzeilen = [
            ("Dashboard", "( 1) anzeigen", "", "", ""),
            ("Studiengang", "( 2) anlegen", "( 3) bearbeiten", "", "( 4) löschen"),
            ("Semester", "( 5) hinzufügen", "( 6) bearbeiten", "", "( 7) löschen"),
            ("Modul", "( 8) hinzufügen", "( 9) bearbeiten", "(10) verschieben", "(11) löschen"),
            ("Prüfungsleistung", "(12) hinzufügen", "(13) bearbeiten", "", "(14) löschen"),
        ]
        # Feste Spaltenbreiten richten die Aktionen auch bei zweistelligen Nummern aus.
        # Leere Einträge halten den Platz für Aktionen frei, die nicht möglich sind.
        for bereich, anlegen, bearbeiten, verschieben, loeschen in menuzeilen:
            print(f"{bereich:<17}{anlegen:<16}{bearbeiten:<16}{verschieben:<17}{loeschen}".rstrip())
        print(f"{'Programm':<17}( 0) beenden")
        print("-" * 78)
        return self.lese_eingabe("Deine Auswahl: ")

    def lese_eingabe(self, text: str) -> str:
        """Liest eine Texteingabe und entfernt Leerzeichen am Anfang und Ende."""
        return input(text).strip()

    def zeige_auswahl(self, titel: str, eintraege: list[str]) -> None:
        """Gibt den Titel und die übergebenen Listeneinträge mit Nummern ab 1 aus."""
        print(f"\n{titel}")
        for nummer, eintrag in enumerate(eintraege, start=1):
            print(f"{nummer:>2}  {eintrag}")

    def zeige_meldung(self, text: str) -> None:
        """Gibt die übergebene Meldung im Terminal aus."""
        print(text)

    def zeige_fehler(self, text: str) -> None:
        """Gibt die übergebene Fehlermeldung mit dem Hinweis "Fehler" aus."""
        print(f"\nFehler: {text}")

    def bestaetige(self, text: str) -> bool:
        """Fragt nach Zustimmung und gibt bei ja oder j den Wert True zurück.

        Groß- und Kleinschreibung spielen keine Rolle. Alle anderen Antworten
        ergeben False.
        """
        antwort = self.lese_eingabe(f"{text} [ja/nein]: ")
        return antwort.casefold() in ("ja", "j")

    def zeige_dashboard(self, daten: dict) -> None:
        """Zeigt die vorbereiteten Kennzahlen und die nach Semestern gegliederten
        Module.

        Die Noten werden für die Anzeige formatiert. Bei einem leeren Dictionary
        erscheint ein Hinweis zum Anlegen des Studiengangs.
        """
        if not daten:
            print("\nNoch kein Studiengang vorhanden. Lege ihn über Menüpunkt 2 an.")
            return

        breite = 78
        print("\n" + "=" * breite)

        # Angaben zu Studiengang inklusive Abschluss
        titel = f"{daten['name']}, {daten['abschluss']}"
        for zeile in wrap(titel, width=breite):
            print(zeile.center(breite))
        print("=" * breite)

        # Angaben zu Notendurchschnitt(en)
        spaltenbreite = breite // 3
        rahmen = "+" + "-" * 16 + "+"
        best_case = formatiere_note(daten["best_case"], 1)
        aktuell = formatiere_note(daten["aktueller_schnitt"], 1)
        worst_case = formatiere_note(daten["worst_case"], 1)
        mitte = f"| {aktuell:^14} |"
        print("\n")
        print(rahmen.center(breite))
        print(f"{best_case:^{spaltenbreite}}{mitte:^{spaltenbreite}}{worst_case:^{spaltenbreite}}")
        print(f"{'best case':^{spaltenbreite}}{rahmen:^{spaltenbreite}}{'worst case':^{spaltenbreite}}")

        # Angaben über ECTS und Prozent
        prozent = f"{daten['fortschritt']:.0f}"
        print()
        print(f"{daten['ects_erreicht']} Punkte ({prozent}%)".center(breite))
        print("\n")
        print("Module".center(breite))

        # Angaben über die Semester und Module inklusive ihrere Noten
        if not daten["semester"]:
            print("\nNoch keine Semester angelegt.")
        for semester in daten["semester"]:
            print(f"\nSemester {semester['nummer']}")
            print("-" * breite)
            if not semester["module"]:
                print("       Noch keine Module angelegt.")
            for modul in semester["module"]:
                note = formatiere_note(modul["note"], 1)
                namenszeilen = wrap(modul["name"], width=breite - 7)
                print(f"{note:<3}    {namenszeilen[0]}")
                for zeile in namenszeilen[1:]:
                    print(f"       {zeile}")
            print()
