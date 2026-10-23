from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    """
    Clase abstracta que sirve de plantilla para todos los extractores de cuotas (scrapers).
    """
    def __init__(self, bookmaker_name):
        self.bookmaker_name = bookmaker_name

    @abstractmethod
    def fetch_odds(self):
        """
        Este método DEBE ser implementado por cada casa de apuestas.
        Debe devolver una lista de diccionarios con los partidos y sus cuotas.
        """
        pass