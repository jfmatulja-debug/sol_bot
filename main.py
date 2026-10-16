import os
import threading
from flask import Flask
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. Servidor web simples para o Render
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Sol Bot esta ativo com Groq!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# 2. Configurações de API
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

client = Groq(api_key=GROQ_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    
    # Modelos padrão ativos na Groq
    modelos = [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "llama-3.1-8b-instant"
    ]
    
    resposta_enviada = False
    erros = []

    for modelo in modelos:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": texto_usuario}],
                model=modelo,
            )
            resposta = chat_completion.choices[0].message.content
            await update.message.reply_text(resposta)
            resposta_enviada = True
            break
        except Exception as e:
            erros.append(f"{modelo}: {str(e)}")
            continue

    if not resposta_enviada:
        await update.message.reply_text(f"Erro ao conectar com Groq:\n{erros[0]}")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
