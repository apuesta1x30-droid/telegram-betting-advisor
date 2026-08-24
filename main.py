import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from core.agent import ask_ai

# Cargar variables de entorno
load_dotenv()

# Configuración básica
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# Inicializar FastAPI
app = FastAPI()

# --- DEFINICIÓN DEL MENÚ INTERACTIVO ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Explicar"), KeyboardButton(text="📊 Interpretar")],
        [KeyboardButton(text="🧮 Comparar"), KeyboardButton(text="🧠 Mentalidad")],
        [KeyboardButton(text="❓ Ayuda / Menú")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Elige una opción o escribe tu pregunta..."
)

# 1. Endpoint BLINDADO para UptimeRobot
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

# 3. Comando /start del bot (Muestra el menú)
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "¡Hola! 👋 Soy tu *Profesor Personal de Apuestas Deportivas*.\n\n"
        "Mi misión es educarte, explicarte conceptos y ayudarte a entender las matemáticas y la psicología detrás de las apuestas.\n\n"
        "Usa el menú de abajo o escribe tus preguntas.",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# 4. Comando /ayuda o botón de Ayuda
@dp.message(Command("ayuda"))
@dp.message(lambda message: message.text == "❓ Ayuda / Menú")
async def cmd_help(message: Message):
    await message.answer(
        "🎓 *COMANDOS DISPONIBLES*\n\n"
        "📖 */explicar [concepto]* - Te enseña qué es y cómo funciona.\n"
        "📊 */interpreta [dato]* - Analiza una estadística o tendencia.\n"
        "🧮 */compara [escenario A] vs [escenario B]* - Calcula el valor matemático.\n"
        "🧠 */mentalidad [situación]* - Consejos para gestionar emociones y rachas.\n\n"
        "También puedes tocar los botones del menú inferior.",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# 5. Comando /ia (Pregunta libre)
@dp.message(Command("ia"))
async def cmd_ia(message: Message):
    question = message.text.replace("/ia", "").strip()
    if not question:
        await message.answer(" *Modo Asesor Activado*\n\nEscribe tu pregunta libre.", parse_mode="Markdown")
        return
    
    await message.answer("🤔 Analizando tu pregunta con IA...")
    response = ask_ai(question)
    await message.answer(response, parse_mode="Markdown")

# 6. Botones del menú (muestran ayuda)
@dp.message(lambda message: message.text == "📖 Explicar")
async def btn_explicar(message: Message):
    await message.answer(
        " *MODO PROFESOR ACTIVADO*\n\n"
        "Escribe el concepto que quieres que te explique.\n\n"
        "Ejemplos:\n"
        "• `Handicap Asiático -1.5`\n"
        "• `Varianza y por qué duele`\n"
        "• `Criterio de Kelly`\n"
        "• `xG (Goles Esperados)`",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "📊 Interpretar")
async def btn_interpreta(message: Message):
    await message.answer(
        "📊 *MODO TRADUCTOR DE DATOS ACTIVADO*\n\n"
        "Pégame el dato, estadística o tendencia que quieras que analice.\n\n"
        "Ejemplos:\n"
        "• `El equipo A tiene un xG de 2.5 pero solo ha marcado 1.0 en los últimos 5 partidos`\n"
        "• `El local ha ganado 8 de sus últimos 10 partidos jugando en casa`",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "🧮 Comparar")
async def btn_compara(message: Message):
    await message.answer(
        " *COMPARADOR DE VALOR (+EV)*\n\n"
        "Compara dos escenarios de apuesta para ver cuál tiene mejor valor matemático.\n\n"
        "Ejemplos:\n"
        "• `1.90 con 60% vs 2.50 con 35%`\n"
        "• `Cuota 2.00 probabilidad 55% contra Cuota 1.75 probabilidad 65%`",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "🧠 Mentalidad")
async def btn_mentalidad(message: Message):
    await message.answer(
        " *MODO COACH MENTAL ACTIVADO*\n\n"
        "Cuéntame tu situación o elige un tema para analizar tu mentalidad de apostador:\n\n"
        "Ejemplos:\n"
        "• `Estoy en racha negativa y quiero recuperar`\n"
        "• `Siento que voy a hacer tilt`\n"
        "• `¿Qué es la falacia del jugador?`\n"
        "• `No consigo seguir mi plan de staking`\n"
        "• `Acabo de perder un bet a última hora (bad beat)`",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# 7. Comandos con texto (procesan la petición)
@dp.message(Command("explicar"))
async def cmd_explicar(message: Message):
    question = message.text.replace("/explicar", "").strip()
    if not question:
        await message.answer(
            "🎓 *MODO PROFESOR ACTIVADO*\n\n"
            "Escribe el concepto que quieres que te explique.\n\n"
            "Ejemplos:\n"
            "• `Handicap Asiático -1.5`\n"
            "• `Varianza y por qué duele`\n"
            "• `Criterio de Kelly`\n"
            "• `xG (Goles Esperados)`",
            parse_mode="Markdown"
        )
        return
    
    await message.answer("📚 Preparando tu lección...")
    educational_prompt = f"Explícame el concepto de '{question}' como si fuera tu alumno. Usa analogías, ejemplos prácticos y formato visual (negritas, listas, emojis). Termina con una pregunta para verificar que lo entendí."
    response = ask_ai(educational_prompt)
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("interpreta"))
async def cmd_interpreta(message: Message):
    data_input = message.text.replace("/interpreta", "").strip()
    if not data_input:
        await message.answer(
            "📊 *MODO TRADUCTOR DE DATOS ACTIVADO*\n\n"
            "Pégame el dato, estadística o tendencia que quieras que analice.\n\n"
            "Ejemplos:\n"
            "• `El equipo A tiene un xG de 2.5 pero solo ha marcado 1.0 en los últimos 5 partidos`\n"
            "• `El local ha ganado 8 de sus últimos 10 partidos jugando en casa`",
            parse_mode="Markdown"
        )
        return
    
    await message.answer("🔍 Analizando los datos y buscando el contexto real...")
    interpret_prompt = f"""Actúa como un analista de datos deportivos experto y profesor. 
    El usuario te proporciona el siguiente dato o estadística: "{data_input}".
    
    Tu tarea:
    1. Explica qué significa esto *realmente* más allá del número superficial.
    2. Menciona conceptos clave aplicables (ej: regresión a la media, varianza, tamaño de muestra).
    3. Indica qué implicaciones tiene esto de cara al futuro.
    
    Usa formato Markdown (*negritas*, listas, emojis). Sé claro, pedagógico y conciso."""
    response = ask_ai(interpret_prompt)
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("compara"))
async def cmd_compara(message: Message):
    comparison_input = message.text.replace("/compara", "").strip()
    if not comparison_input:
        await message.answer(
            "🧮 *COMPARADOR DE VALOR (+EV)*\n\n"
            "Compara dos escenarios de apuesta para ver cuál tiene mejor valor matemático.\n\n"
            "Ejemplos:\n"
            "• `1.90 con 60% vs 2.50 con 35%`\n"
            "• `Cuota 2.00 probabilidad 55% contra Cuota 1.75 probabilidad 65%`",
            parse_mode="Markdown"
        )
        return
    
    await message.answer(" Calculando valor esperado de ambos escenarios...")
    compare_prompt = f"""Actúa como un profesor experto en matemáticas de apuestas.
    El usuario quiere comparar estos dos escenarios: "{comparison_input}".
    
    Tu tarea:
    1. **Extrae los datos**: Identifica las cuotas y probabilidades de cada escenario.
    2. **Calcula el EV** de cada uno: EV = (Probabilidad × (Cuota - 1)) - (1 - Probabilidad)
    3. **Calcula la probabilidad implícita**: Prob_Implícita = 1 / Cuota
    4. **Compara**: ¿Cuál tiene mejor EV? ¿Cuál tiene valor positivo (+EV)?
    5. **Explica pedagógicamente**: Por qué una es mejor que la otra.
    
    Usa formato Markdown con *negritas*, listas y emojis. Muestra los cálculos de forma clara."""
    response = ask_ai(compare_prompt)
    await message.answer(response, parse_mode="Markdown")

@dp.message(Command("mentalidad"))
async def cmd_mentalidad(message: Message):
    text = message.text.replace("/mentalidad", "").strip()
    if not text:
        await message.answer(
            "🧠 *MODO COACH MENTAL ACTIVADO*\n\n"
            "Cuéntame tu situación o elige un tema para analizar tu mentalidad de apostador:\n\n"
            "Ejemplos:\n"
            "• `Estoy en racha negativa y quiero recuperar`\n"
            "• `Siento que voy a hacer tilt`\n"
            "• `¿Qué es la falacia del jugador?`\n"
            "• `No consigo seguir mi plan de staking`\n"
            "• `Acabo de perder un bet a última hora (bad beat)`",
            reply_markup=main_menu,
            parse_mode="Markdown"
        )
        return
    
    await message.answer("🧠 Analizando tu estado mental y preparándote un consejo...")
    mental_prompt = f"""Actúa como un coach de psicología deportiva especializado en traders y apostadores profesionales.
    El usuario te presenta la siguiente situación mental o duda: "{text}".
    
    Tu tarea:
    1. Valida sus emociones (es normal sentirse así).
    2. Explica el sesgo cognitivo o trampa mental en la que puede estar cayendo (ej. falacia del jugador, aversión a la pérdida, tilt).
    3. Dale un consejo práctico e inmediato para volver a la disciplina y al pensamiento matemático (+EV).
    4. Recuérdale que el resultado a corto plazo es varianza, pero el proceso a largo plazo es lo que da beneficios.
    
    Usa formato Markdown (*negritas*, listas, emojis). Sé empático pero firme. Máximo 15-20 líneas."""
    response = ask_ai(mental_prompt)
    await message.answer(response, parse_mode="Markdown")

# Handler genérico para mensajes de texto libre (sin comando)
@dp.message(lambda message: message.text and not message.text.startswith("/"))
async def handle_text(message: Message):
    # Si el usuario escribe texto libre, lo tratamos como una pregunta para la IA
    user_text = message.text.strip()
    
    if not user_text:
        return
    
    await message.answer(" Pensando...")
    response = ask_ai(user_text)
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
