import os
import threading
from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Servidor web simples para o Render aceitar no plano gratuito
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Sol Bot está ativo!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# 2. Configuração do Gemini e do Telegram
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=texto_usuario,
    )
    await update.message.reply_text(response.text)

if __name__ == "__main__":
    # Inicia o servidor web em segundo plano
    threading.Thread(target=run_web, daemon=True).start()
    
    # Inicia o robô do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
