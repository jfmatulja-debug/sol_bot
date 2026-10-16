import os
import threading
from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Servidor web simples para manter o Render ativo
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
    
    # Lista de modelos oficiais compativeis com a SDK google-genai
    modelos = [
        'gemini-2.5-flash',
        'gemini-1.5-flash',
        'gemini-2.5-pro'
    ]
    
    resposta_texto = None

    for modelo in modelos:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=texto_usuario,
            )
            if response and response.text:
                resposta_texto = response.text
                break
        except Exception as err:
            # Imprime o erro real no log do Render para diagnostico
            print(f"Erro no modelo {modelo}: {err}")
            continue

    if resposta_texto:
        await update.message.reply_text(resposta_texto)
    else:
        await update.message.reply_text(
            "Não foi possível obter resposta no momento. Por favor, tente novamente em instantes."
        )

if __name__ == "__main__":
    # Inicia o servidor Web em segundo plano
    threading.Thread(target=run_web, daemon=True).start()
    
    # Inicia o bot do Telegram
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
