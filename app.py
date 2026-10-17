"""Erzeugt und verdrahtet die Klassen"""

from pathlib import Path

from controller import DashboardController
from repository import CsvStudiengangRepository
from service import NotenService
from view import KonsolenView


class DashboardApp:
    """Setzt die Anwendung aus Repository, Service, View und Controller zusammen."""

    def __init__(self) -> None:
        """Richtet die Anwendung ein und verbindet ihre Objekte. Die Attribute mit self speichern die zugehörigen Objekte. Der Datenordner liegt auf gleicher Ebene der Python-Datei.
        """
        programmordner = Path(__file__).resolve().parent
        self.repository = CsvStudiengangRepository(programmordner / "daten")
        self.service = NotenService()
        self.view = KonsolenView()
        self.controller = DashboardController(self.repository, self.service, self.view)

    def start(self) -> None:
        """Startet den Controller, der die Daten lädt und die Menübedienung übernimmt."""
        self.controller.start()
