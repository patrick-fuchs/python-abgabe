"""Berechnung der Kennzahlen"""

from domain import Studiengang


class NotenService:
    """Berechnet Notendurchschnitte und erreichte ECTS aus den Domain-Objekten."""

    def summiere_bestandene_module(self, studiengang: Studiengang) -> tuple[float, int]:
        """Summiert die gewichteten Noten und die ECTS aktuell bestandener Module.

        Gibt zuerst die Summe aus Note mal Modul-ECTS und danach die ECTS-Summe
        zurück. Pro Modul zählt nur die neueste Prüfungsnote.
        """
        notensumme = 0.0
        ects_summe = 0
        for modul in studiengang.gib_alle_module():
            note = modul.aktuelle_note()
            if note is not None and note <= 4.0:
                # Die ECTS gewichten die Note. Ein Modul zählt genau einmal.
                notensumme += note * modul.gib_ects()
                ects_summe += modul.gib_ects()
        return notensumme, ects_summe

    def berechne_erreichte_ects(self, studiengang: Studiengang) -> int:
        """Gibt die Summe der ECTS-Punkte aller aktuell bestandenen Module zurück."""
        notensumme, ects_summe = self.summiere_bestandene_module(studiengang)
        return ects_summe

    def berechne_aktuellen_schnitt(self, studiengang: Studiengang) -> float | None:
        """Gibt den nach ECTS gewichteten Schnitt der aktuell bestandenen Module
        zurück.

        Ohne bestandene Module wird None zurückgegeben.
        """
        notensumme, ects_summe = self.summiere_bestandene_module(studiengang)
        if ects_summe == 0:
            return None
        return notensumme / ects_summe

    def berechne_prognose(self, studiengang: Studiengang, offene_note: float) -> float:
        """Berechnet den Gesamtschnitt für eine angenommene Note aller offenen ECTS.

        offene_note ist die angenommene Note. Zu den offenen ECTS zählen auch Punkte
        von Modulen, die noch nicht angelegt wurden.
        """
        notensumme, erreichte_ects = self.summiere_bestandene_module(studiengang)
        gesamt_ects = studiengang.gib_ects_gesamt()
        # Auch noch nicht angelegte Module gehören zu den offenen ECTS.
        offene_ects = gesamt_ects - erreichte_ects
        return (notensumme + offene_ects * offene_note) / gesamt_ects

    def berechne_best_case(self, studiengang: Studiengang) -> float | None:
        """Berechnet den möglichen Gesamtschnitt bei einer Note von 1,0 für alle
        offenen ECTS.
        """
        return self.berechne_prognose(studiengang, 1.0)

    def berechne_worst_case(self, studiengang: Studiengang) -> float | None:
        """Berechnet den möglichen Gesamtschnitt bei einer bestandenen Note von 4,0 für
        alle offenen ECTS.
        """
        return self.berechne_prognose(studiengang, 4.0)
