import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración básica
logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# Inicializar FastAPI (necesario para Render Free Tier)
app = FastAPI()

# 1. Endpoint para UptimeRobot (mantiene el bot despierto)
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Bot is alive and running!"}

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
        "/ayuda - Mostrar este mensaje\n\n"
        "💡 *Próximamente:*\n"
        "/analizar [partido] - Buscar valor en las cuotas\n"
        "/explicar [término] - Aprender conceptos de apuestas"
    )

# Función que se ejecuta al iniciar la aplicación en Render
@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url and webhook_url != "https://tu-app.onrender.com":
        await bot.set_webhook(f"{webhook_url}/webhook")
        logging.info(f"Webhook establecido en: {webhook_url}/webhook")
    else:
        logging.warning("WEBHOOK_URL no configurada correctamente. El bot no recibirá mensajes.")
