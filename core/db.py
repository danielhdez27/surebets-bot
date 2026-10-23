import sqlite3
from datetime import datetime

# El archivo de la base de datos se creará automáticamente en la carpeta de tu proyecto
DB_NAME = "historico_cuotas.db"

def init_db():
    """Conecta con la base de datos y crea la tabla si es la primera vez que se ejecuta."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Estructura de la tabla para analizar cómo fluctúan los precios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS odds_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_escaneo TEXT,
            deporte TEXT,
            partido TEXT,
            cuota_1 REAL,
            casa_1 TEXT,
            cuota_x REAL,
            casa_x TEXT,
            cuota_2 REAL,
            casa_2 TEXT,
            roi REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_odds(deporte, partido, c1, casa1, cx, casax, c2, casa2, roi):
    """Inserta una nueva fila con la "foto" de las cuotas en el momento del escaneo."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Generamos la marca de tiempo exacta
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO odds_history 
        (fecha_escaneo, deporte, partido, cuota_1, casa_1, cuota_x, casa_x, cuota_2, casa_2, roi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha, deporte, partido, c1, casa1, cx, casax, c2, casa2, roi))
    
    conn.commit()
    conn.close()