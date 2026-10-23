import re
import difflib
import unicodedata

def normalize_name(name):
    """
    Limpia y estandariza el nombre de un equipo para facilitar la comparación.
    """
    # Pasamos a minúsculas
    name = name.lower()
    
    # Quitamos tildes y acentos (ej: Atlético -> Atletico)
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                  if unicodedata.category(c) != 'Mn')
    
    # Quitamos caracteres especiales, dejando solo letras y números
    name = re.sub(r'[^a-z0-9\s]', '', name)
    
    # Eliminamos términos genéricos que las casas de apuestas suelen añadir o quitar
    terms_to_remove = ['fc', 'cf', 'cd', 'real', 'atletico', 'athletic', 'club', 'balompie', 'ud']
    for term in terms_to_remove:
        # Usamos regex con límites de palabra para no cortar nombres (ej: no quitar 'real' de 'realidad')
        name = re.sub(rf'\b{term}\b', '', name)
    
    # Quitamos espacios dobles y espacios a los lados
    return " ".join(name.split())

def is_match(name1, name2, threshold=0.80):
    """
    Compara dos nombres y devuelve True si se parecen más que el porcentaje indicado (threshold).
    """
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    # Compara la similitud de las dos cadenas de texto normalizadas
    similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
    
    return similarity >= threshold, round(similarity, 2)