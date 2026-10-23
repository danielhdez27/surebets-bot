import requests
from config import ODDS_API_KEY, BOOKMAKERS

def get_best_odds_for_sport(sport_key):
    """Descarga un deporte y extrae la mejor cuota combinada del mercado 1X2."""
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu,uk", # Extraemos casas de Europa y UK
        "markets": "h2h",   # Mercado 1X2 (Head to Head)
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error API ({sport_key}): {response.text}")
            return []
            
        partidos_optimizados = []
        
        for evento in response.json():
            home = evento["home_team"]
            away = evento["away_team"]
            
            # Variables para guardar la cuota más alta y qué casa la ofrece
            best_1 = {"price": 0.0, "bookie": ""}
            best_X = {"price": 0.0, "bookie": ""}
            best_2 = {"price": 0.0, "bookie": ""}
            
            for bookie in evento.get("bookmakers", []):
                if bookie["key"] in BOOKMAKERS:
                    for market in bookie.get("markets", []):
                        if market["key"] == "h2h":
                            for outcome in market["outcomes"]:
                                price = outcome["price"]
                                # Filtramos la mejor cuota para el local, empate y visitante
                                if outcome["name"] == home and price > best_1["price"]:
                                    best_1 = {"price": price, "bookie": bookie["title"]}
                                elif outcome["name"] == "Draw" and price > best_X["price"]:
                                    best_X = {"price": price, "bookie": bookie["title"]}
                                elif outcome["name"] == away and price > best_2["price"]:
                                    best_2 = {"price": price, "bookie": bookie["title"]}
                                    
            # Solo guardamos el partido si encontramos cuotas para los 3 resultados
            if best_1["price"] > 0 and best_X["price"] > 0 and best_2["price"] > 0:
                partidos_optimizados.append({
                    'match': f"{home} vs {away}",
                    'sport': sport_key,
                    'best_1': best_1,
                    'best_X': best_X,
                    'best_2': best_2
                })
                
        return partidos_optimizados
    except Exception as e:
        print(f"Error de conexión: {e}")
        return []