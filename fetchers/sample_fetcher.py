from fetchers.base import BaseFetcher

class WinamaxFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("Winamax")

    def fetch_odds(self):
        # Datos simulados simulando lo que extraeríamos de la web de Winamax
        return [
            {'match': 'Real Madrid vs FC Barcelona', 'market': '1X2', 'odds': [2.80, 3.50, 2.50]},
            {'match': 'Atletico de Madrid vs Sevilla', 'market': '1X2', 'odds': [1.80, 3.20, 4.00]}
        ]

class CodereFetcher(BaseFetcher):
    def __init__(self):
        super().__init__("Codere")

    def fetch_odds(self):
        # Datos simulados de Codere. 
        # Fíjate que el nombre del primer partido está escrito diferente.
        # Además, paga 3.20 por la victoria del Madrid. Si apuestas al 1 en Codere (3.20), 
        # a la X en Winamax (3.50) y al 2 en Winamax (2.50), hay una surebet asegurada.
        return [
            {'match': 'R. Madrid vs Barcelona', 'market': '1X2', 'odds': [3.20, 3.10, 2.20]},
            {'match': 'Atlético Madrid vs Sevilla FC', 'market': '1X2', 'odds': [1.75, 3.30, 4.20]}
        ]