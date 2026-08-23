import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from core.agent import ask_ai
from data.odds_api import get_odds

# Cargar variables de entorno
load_dotenv()

# Configuración básica
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# Inicializar FastAPI
app = FastAPI()

# 1. Endpoint BLINDADO para UptimeRobot y Render (acepta GET, HEAD, POST, etc.)
@app.api_route("/", methods=["GET", "POST", "HEAD", "PUT", "DELETE"])
@app.api_route("/health", methods=["GET", "POST", "HEAD", "PUT", "DELETE"])
async def health_check():
    return JSONResponse(content={"status": "ok", "message": "Bot is alive and running!"})

# 2. Endpoint para recibir mensajes de Telegram (Webhook)
@app.post("/webhook")
async def webhook(request: Request):
    update = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

# 3. Comando /start del bot
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "¡Hola! 👋 Soy tu Asesor de Apuestas Deportivas con IA.\n\n"
        "Estoy aquí para ayudarte a:\n"
        "✅ Analizar valor en las cuotas (+EV)\n"
        "✅ Explicar conceptos y términos de apuestas\n"
        "✅ Gestionar tu bankroll de forma responsable\n\n"
        "Escribe /ayuda para ver lo que puedo hacer."
    )

# 4. Comando /ayuda
@dp.message(Command("ayuda"))
async def cmd_help(message: Message):
    await message.answer(
        "📚 *Comandos disponibles:*\n"
        "/start - Iniciar el bot\n"
        "/ayuda - Mostrar este mensaje\n"
        "/ia [tu pregunta] - Preguntar al asesor de IA\n\n"
        "💡 *Próximamente:*\n"
        "/analizar [partido] - Buscar valor en las cuotas"
    )

# 5. Comando /ia para preguntar al asesor
@dp.message(Command("ia"))
async def cmd_ia(message: Message):
    question = message.text.replace("/ia", "").strip()
    
    if not question:
        await message.answer(
            "🧠 *Modo Asesor Activado*\n\n"
            "Por favor, escribe tu pregunta después del comando.\n"
            "Ejemplos:\n"
            "• `/ia ¿Qué es el valor esperado (+EV)?`\n"
            "• `/ia Dame un consejo para gestionar mi bankroll`\n"
            "• `/ia ¿Por qué es malo apostar siempre al favorito?`"
        )
        return
    
    thinking_msg = await message.answer("🤔 Analizando tu pregunta con IA...")
    response = ask_ai(question)
       
    await message.answer(response, parse_mode="Markdown")

# Función que se ejecuta al iniciar la aplicación en Render
@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url and "onrender.com" in webhook_url:
        await bot.set_webhook(f"{webhook_url}/webhook")
        logging.info(f"Webhook establecido en: {webhook_url}/webhook")
    else:
        logging.warning("WEBHOOK_URL no configurada correctamente.")

# 6. Comando /cuotas para probar la API
@dp.message(Command("cuotas"))
async def cmd_cuotas(message: Message):
    thinking_msg = await message.answer("📡 Conectando con las casas de apuestas...")
    
    # Pedimos cuotas de La Liga (fútbol español)
    odds_data = get_odds(sport_key="soccer_spain_la_liga")
    
    if not odds_data:
        await message.answer("⚠️ No se pudieron obtener datos. Verifica la API Key o que haya partidos hoy.")
        return
        
    # Formateamos la respuesta para Telegram
    response = "⚽ *PARTIDOS DE LA LIGA (Cuotas 1X2)*\n\n"
    
    # Mostramos solo los primeros 5 partidos para no saturar
    for match in odds_data[:5]:
        home_team = match.get("home_team", "Desconocido")
        away_team = match.get("away_team", "Desconocido")
        
        # Buscamos las cuotas en los bookmakers
        bookmakers = match.get("bookmakers", [])
        odds_text = "Cuotas no disponibles"
        
        if bookmakers:
            # Tomamos el primer bookmaker que tenga el mercado h2h
            for bm in bookmakers:
                if bm.get("key") == "pinnacle":  # Usamos Pinnacle como referencia
                    markets = bm.get("markets", [])
                    for m in markets:
                        if m.get("key") == "h2h":
                            outcomes = m.get("outcomes", [])
                            home_odd = next((o["price"] for o in outcomes if o["name"] == home_team), "N/A")
                            draw_odd = next((o["price"] for o in outcomes if o["name"] == "Draw"), "N/A")
                            away_odd = next((o["price"] for o in outcomes if o["name"] == away_team), "N/A")
                            odds_text = f"1: {home_odd} | X: {draw_odd} | 2: {away_odd}"
                            break
                if odds_text != "Cuotas no disponibles":
                    break
        
        response += f"🆚 *{home_team} vs {away_team}*\n{odds_text}\n\n"
    
    response += "_(Mostrando primeros 5 partidos)_"
    
    await message.answer(response, parse_mode="Markdown")

# 8. Comando /explicar (El Profesor)
@dp.message(Command("explicar"))
async def cmd_explicar(message: Message):
    # Obtenemos el texto después de "/explicar"
    question = message.text.replace("/explicar", "").strip()
    
    if not question:
        await message.answer(
            "🎓 *MODO PROFESOR ACTIVADO*\n\n"
            "Escribe el concepto que quieres que te explique.\n\n"
            "Ejemplos:\n"
            "• `/explicar Handicap Asiático -1.5`\n"
            "• `/explicar Varianza y por qué duele`\n"
            "• `/explicar Criterio de Kelly`\n"
            "• `/explicar xG (Goles Esperados)`\n"
            "• `/explicar CLV (Closing Line Value)`",
            parse_mode="Markdown"
        )
        return
    
    # Avisamos que estamos preparando la clase
    thinking_msg = await message.answer("📚 Preparando tu lección...")
    
    # Añadimos contexto educativo al prompt
    educational_prompt = f"Explícame el concepto de '{question}' como si fuera tu alumno. Usa analogías, ejemplos prácticos y formato visual (negritas, listas, emojis). Termina con una pregunta para verificar que lo entendí."
    
    # Consultamos a la IA
    response = ask_ai(educational_prompt)
    
    # Respondemos al alumno
    await message.answer(response, parse_mode="Markdown")

# 9. Comando /interpreta (Traductor de Datos)
@dp.message(Command("interpreta"))
async def cmd_interpreta(message: Message):
    # Obtenemos el texto después de "/interpreta"
    data_input = message.text.replace("/interpreta", "").strip()
    
    if not data_input:
        await message.answer(
            "📊 *MODO TRADUCTOR DE DATOS ACTIVADO*\n\n"
            "Pégame el dato, estadística o tendencia que quieras que analice.\n\n"
            "Ejemplos:\n"
            "• `/interpreta El equipo A tiene un xG de 2.5 pero solo ha marcado 1.0 en los últimos 5 partidos`\n"
            "• `/interpreta El local ha ganado 8 de sus últimos 10 partidos jugando en casa`\n"
            "• `/interpreta La cuota ha bajado de 2.10 a 1.85 en las últimas 2 horas`",
            parse_mode="Markdown"
        )
        return
    
    # Avisamos que estamos analizando
    thinking_msg = await message.answer("🔍 Analizando los datos y buscando el contexto real...")
    
    # Prompt específico para interpretación de datos
    interpret_prompt = f"""Actúa como un analista de datos deportivos experto y profesor. 
    El usuario te proporciona el siguiente dato o estadística: "{data_input}".
    
    Tu tarea:
    1. Explica qué significa esto *realmente* más allá del número superficial.
    2. Menciona conceptos clave aplicables (ej: regresión a la media, varianza, tamaño de muestra, contexto táctico, movimiento de mercado).
    3. Indica qué implicaciones tiene esto de cara al futuro o cómo debería influir en la toma de decisiones.
    
    Usa formato Markdown (*negritas*, listas, emojis). Sé claro, pedagógico y conciso (máx. 15-20 líneas)."""
    
    # Consultamos a la IA
    response = ask_ai(interpret_prompt)
    
    # Respondemos al alumno
    await message.answer(response, parse_mode="Markdown")

    # 10. Comando /compara (Comparador de Valor)
@dp.message(Command("compara"))
async def cmd_compara(message: Message):
    # Obtenemos el texto después de "/compara"
    comparison_input = message.text.replace("/compara", "").strip()
    
    if not comparison_input:
        await message.answer(
            " *COMPARADOR DE VALOR (+EV)*\n\n"
            "Compara dos escenarios de apuesta para ver cuál tiene mejor valor matemático.\n\n"
            "Formato: `/compara [Cuota1] con [Prob1]% vs [Cuota2] con [Prob2]%`\n\n"
            "Ejemplos:\n"
            "• `/compara 1.90 con 60% vs 2.50 con 35%`\n"
            "• `/compara Cuota 2.00 probabilidad 55% contra Cuota 1.75 probabilidad 65%`\n"
            "• `/compara Apostar al favorito 1.50 (70%) vs al underdog 3.00 (30%)`",
            parse_mode="Markdown"
        )
        return
    
    # Avisamos que estamos calculando
    thinking_msg = await message.answer("🧮 Calculando valor esperado de ambos escenarios...")
    
    # Prompt específico para comparación de valor
    compare_prompt = f"""Actúa como un profesor experto en matemáticas de apuestas.
    El usuario quiere comparar estos dos escenarios: "{comparison_input}".
    
    Tu tarea:
    1. **Extrae los datos**: Identifica las cuotas y probabilidades de cada escenario.
    2. **Calcula el EV** de cada uno usando la fórmula: EV = (Probabilidad × (Cuota - 1)) - (1 - Probabilidad)
    3. **Calcula la probabilidad implícita** de cada cuota: Prob_Implícita = 1 / Cuota
    4. **Compara**: ¿Cuál tiene mejor EV? ¿Cuál tiene valor positivo (+EV)?
    5. **Explica pedagógicamente**: Por qué una es mejor que la otra, incluso si la "obvia" no es la mejor matemáticamente.
    
    Usa formato Markdown con *negritas*, listas y emojis. Muestra los cálculos de forma clara.
    Termina con una recomendación clara sobre cuál elegiría un apostador profesional."""
    
    # Consultamos a la IA
    response = ask_ai(compare_prompt)
    
    # Respondemos al alumno
    await message.answer(response, parse_mode="Markdown")
