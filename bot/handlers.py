import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from fetchers.api_fetcher import get_best_odds_for_sport
from core.surebet import check_3way
from core.user_settings import get_user_prefs, update_min_roi
from config import SPORTS, BOOKMAKERS
from core.db import insert_odds

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Usa /scan para buscar oportunidades o /settings para filtrar el beneficio mínimo.")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un menú con botones para elegir el ROI mínimo."""
    keyboard = [
        [
            InlineKeyboardButton("ROI > 0%", callback_data='roi_0'),
            InlineKeyboardButton("ROI > 2%", callback_data='roi_2'),
            InlineKeyboardButton("ROI > 5%", callback_data='roi_5'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Selecciona el beneficio (ROI) mínimo que deseas buscar:', reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta qué botón ha pulsado el usuario y actualiza la configuración."""
    query = update.callback_query
    await query.answer() # Esto evita que el botón se quede "cargando" visualmente
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'roi_0':
        update_min_roi(user_id, 0.0)
        await query.edit_message_text(text="✅ Filtro actualizado: Avisaré de TODAS las surebets.")
    elif data == 'roi_2':
        update_min_roi(user_id, 2.0)
        await query.edit_message_text(text="✅ Filtro actualizado: Solo surebets con ROI superior al 2%.")
    elif data == 'roi_5':
        update_min_roi(user_id, 5.0)
        await query.edit_message_text(text="✅ Filtro actualizado: Solo surebets muy altas (ROI > 5%).")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    min_roi = get_user_prefs(user_id)["min_roi"]
    await update.message.reply_text(f"Escaneando {len(SPORTS)} ligas combinando {len(BOOKMAKERS)} casas (Filtro: > {min_roi}% ROI)... ⏳")

    found = False
    for sport in SPORTS:
        partidos = get_best_odds_for_sport(sport)

        for p in partidos:
            # Mandamos las mejores cuotas absolutas al motor matemático
            resultado = check_3way(p['best_1']['price'], p['best_X']['price'], p['best_2']['price'])
            
            # --- NUEVO: GUARDAMOS EL REGISTRO EN LA BASE DE DATOS ---
            insert_odds(
                p['sport'], p['match'], 
                p['best_1']['price'], p['best_1']['bookie'],
                p['best_X']['price'], p['best_X']['bookie'],
                p['best_2']['price'], p['best_2']['bookie'],
                resultado['roi']
            )

            if resultado["is_surebet"] and resultado["roi"] >= min_roi:
                found = True
                mensaje = (
                    f"🚨 ¡SUREBET ENCONTRADA! 🚨\n"
                    f"⚽ Partido: {p['match']}\n"
                    f"🏆 Liga: {p['sport']}\n"
                    f"💰 Beneficio seguro (ROI): {resultado['roi']}%\n\n"
                    f"💶 Qué apostar (para 100€):\n"
                    f"   - 1 ({p['best_1']['bookie']} @{p['best_1']['price']}): {resultado['stakes'][0]}€\n"
                    f"   - X ({p['best_X']['bookie']} @{p['best_X']['price']}): {resultado['stakes'][1]}€\n"
                    f"   - 2 ({p['best_2']['bookie']} @{p['best_2']['price']}): {resultado['stakes'][2]}€"
                )
                await update.message.reply_text(mensaje)

    if not found:
        await update.message.reply_text("No se encontraron surebets en este escaneo.")

# --- NUEVAS FUNCIONES PARA EL ESCÁNER AUTOMÁTICO ---

async def auto_scan(context: ContextTypes.DEFAULT_TYPE):
    """Esta función la ejecuta el bot solo en segundo plano."""
    job = context.job
    chat_id = job.chat_id
    user_id = chat_id # En chats privados, el ID de usuario y el chat coinciden
    
    # Leemos la configuración del usuario
    min_roi = get_user_prefs(user_id)["min_roi"]
    
    # Recorremos todas las ligas configuradas (La Liga, Premier, Champions...)
    for sport in SPORTS:
        partidos = get_best_odds_for_sport(sport)
        
        for p in partidos:
            # Mandamos las mejores cuotas absolutas al motor matemático
            resultado = check_3way(p['best_1']['price'], p['best_X']['price'], p['best_2']['price'])
            
            # APLICAMOS EL FILTRO: Solo avisamos si es surebet Y supera el ROI
            if resultado["is_surebet"] and resultado["roi"] >= min_roi:
                mensaje = (
                    f"🤖 [AUTO] 🚨 ¡NUEVA SUREBET! 🚨\n"
                    f"⚽ Partido: {p['match']}\n"
                    f"🏆 Liga: {p['sport']}\n"
                    f"💰 Beneficio seguro (ROI): {resultado['roi']}%\n\n"
                    f"💶 Qué apostar (para 100€):\n"
                    f"   - 1 ({p['best_1']['bookie']} @{p['best_1']['price']}): {resultado['stakes'][0]}€\n"
                    f"   - X ({p['best_X']['bookie']} @{p['best_X']['price']}): {resultado['stakes'][1]}€\n"
                    f"   - 2 ({p['best_2']['bookie']} @{p['best_2']['price']}): {resultado['stakes'][2]}€"
                )
                # Enviamos el mensaje al chat
                await context.bot.send_message(chat_id=chat_id, text=mensaje)

async def start_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para encender el radar en modo francotirador (Solo fin de semana)."""
    chat_id = update.effective_message.chat_id
    
    # Limpiamos radares anteriores
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    # Fijamos la hora de España peninsular
    zona_horaria = pytz.timezone('Europe/Madrid')
    
    # En Python los días van del 0 (Lunes) al 6 (Domingo)
    horas_viernes = [17, 19, 20]
    horas_finde = [12, 14, 16, 18, 19, 20, 21]
    
    # 1. Programamos los 3 disparos del Viernes (día 4)
    for h in horas_viernes:
        momento = datetime.time(hour=h, minute=0, tzinfo=zona_horaria)
        context.job_queue.run_daily(auto_scan, time=momento, days=(4,), chat_id=chat_id, name=str(chat_id))
        
    # 2. Programamos los 14 disparos del Sábado (5) y Domingo (6)
    for h in horas_finde:
        momento = datetime.time(hour=h, minute=0, tzinfo=zona_horaria)
        context.job_queue.run_daily(auto_scan, time=momento, days=(5, 6), chat_id=chat_id, name=str(chat_id))
        
    await update.message.reply_text(
        "🎯 Modo Francotirador activado.\n"
        "El radar disparará 17 veces cada fin de semana (Vie-Dom) en los picos de volatilidad."
    )

async def stop_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para apagar el radar."""
    chat_id = update.effective_message.chat_id
    
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    for job in current_jobs:
        job.schedule_removal()
        
    await update.message.reply_text("🛑 Radar en segundo plano detenido.")