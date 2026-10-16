import os
import threading
from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Servidor web simples para manter o Render ativo no plano Free
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Sol Bot esta ativo e rodando!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# 2. Configuração do Gemini e Telegram
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = genai.Client(api_key=GEMINI_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    
    # Lista de modelos por ordem de tentativa
    # Se um falhar por cota, erro 503 ou 404, o bot tenta o próximo imediatamente
    modelos = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-1.5-pro'
    ]
    
    resposta_enviada = False

    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=texto_usuario,
            )
            if response.text:
                await update.message.reply_text(response.text)
                resposta_enviada = True
                break
        except Exception:
            # Se der erro no modelo atual (503, 404, cota, etc.), ignora e tenta o proximo
            continue

    if not resposta_enviada:
        await update.message.reply_text(
            "Desculpe, todos os modelos do Gemini estão temporariamente indisponíveis. Por favor, tente novamente em instantes."
        )

if __name__ == "__main__":
    # Inicia o servidor Web em segundo plano
    threading.Thread(target=run_web, daemon=True).start()
    
    # Inicia o bot do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
