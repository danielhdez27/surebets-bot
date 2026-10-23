# Diccionario para guardar en memoria la configuración de cada usuario
user_prefs = {}

def get_user_prefs(user_id):
    """Devuelve las preferencias del usuario. Por defecto, ROI > 0%."""
    if user_id not in user_prefs:
        user_prefs[user_id] = {"min_roi": 0.0}
    return user_prefs[user_id]

def update_min_roi(user_id, new_roi):
    """Actualiza el ROI mínimo que exige el usuario."""
    prefs = get_user_prefs(user_id)
    prefs["min_roi"] = new_roi