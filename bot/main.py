import sys
import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Esta línea soluciona los problemas de rutas. 
# TIENE que ejecutarse antes de importar tus módulos personalizados.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ahora sí, importamos nuestras cosas de core y config
from config import TELEGRAM_TOKEN
import bot.handlers as handlers
from core.db import init_db  # <--- COLOCA ESTA LÍNEA AQUÍ

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main():
    if TELEGRAM_TOKEN == "PEGA_AQUI_TU_TOKEN":
        print("⚠️ ERROR: No has puesto tu Token real en config.py")
        return

    print("🟢 Bot arrancando con menús interactivos...")
    init_db()
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registramos los comandos antiguos y los nuevos
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("scan", handlers.scan))
    app.add_handler(CommandHandler("settings", handlers.settings))
    app.add_handler(CommandHandler("start_auto", handlers.start_auto)) # NUEVO
    app.add_handler(CommandHandler("stop_auto", handlers.stop_auto))   # NUEVO
    
    # Registramos el detector de pulsaciones en los botones
    app.add_handler(CallbackQueryHandler(handlers.button_handler))

    app.run_polling()

if __name__ == '__main__':
    main()