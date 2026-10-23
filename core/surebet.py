def calculate_arbitrage(odds, total_bankroll=100):
    """
    Calcula si una lista de cuotas forma una surebet y cómo repartir el dinero.
    """
    # Calculamos el margen total sumando la inversa de cada cuota
    margin = sum(1 / odd for odd in odds)
    
    # Si el margen es mayor o igual a 1, la casa tiene ventaja (no hay surebet)
    if margin >= 1:
        return {"is_surebet": False, "roi": 0, "stakes": []}
    
    # Si es menor a 1, calculamos el beneficio (ROI)
    roi = (1 / margin - 1) * 100
    
    # Calculamos cuánto apostar a cada cuota para asegurar el mismo beneficio
    stakes = [(total_bankroll / odd) / margin for odd in odds]
    
    return {
        "is_surebet": True,
        "roi": round(roi, 2),
        "margin": round(margin, 4),
        "stakes": [round(s, 2) for s in stakes]
    }

def check_2way(odd1, odd2, bankroll=100):
    """Para mercados de 2 opciones (ej: Tenis, o Más/Menos goles)"""
    return calculate_arbitrage([odd1, odd2], bankroll)

def check_3way(c1, cx, c2):
    # Aseguramos que operamos con decimales
    c1, cx, c2 = float(c1), float(cx), float(c2)
    
    # 1. Calculamos el margen total del mercado
    margin = (1 / c1) + (1 / cx) + (1 / c2)
    
    # 2. Calculamos el ROI real (si el margen es > 1, el ROI saldrá negativo automáticamente)
    roi = round((1 / margin - 1) * 100, 2)
    
    # 3. Solo es surebet si el margen es menor a 1 (menos del 100%)
    is_surebet = margin < 1.0
    
    # 4. Calculamos cuánto habría que apostar para invertir 100€ en total
    stakes = [
        round((100 / margin) / c1, 2),
        round((100 / margin) / cx, 2),
        round((100 / margin) / c2, 2)
    ]
    
    return {
        "is_surebet": is_surebet,
        "roi": roi,         # ¡Ahora esto devolverá cosas como -4.56!
        "stakes": stakes
    }