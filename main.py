import os
import random
import logging
from groq import Groq
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

# ================= CONFIG =================
TOKEN = os.getenv("BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_KEY)

logging.basicConfig(level=logging.INFO)

# ============== PERSONALIDADE =============
SYSTEM_PROMPT = (
    "Você se chama Malu. "
    "Você é jovem, simpática e zoeira. "
    "Responda em português do Brasil. "
    "Use frases completas e naturais. "
    "Fale como alguém de grupo. "
    "No máximo 2 emojis."
)

# ============== RESPOSTAS RÁPIDAS =========
RESPOSTAS_RAPIDAS = {
    "oi": ["E aí! 😄", "Oi! Cheguei 😎"],
    "bom dia": ["Bom diaaa ☀️", "Bora acordar 😅"],
    "boa noite": ["Boa noite 😴", "Até amanhã 👋"],
    "kkkk": ["Rindo junto 😂", "Essa foi boa 😅"],
}

# ============== IA =========================
def perguntar_ia(texto):
    try:
        chat = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto}
            ],
            temperature=0.6,
            max_tokens=80
        )

        resposta = chat.choices[0].message.content.strip()

        if not resposta:
            return random.choice([
                "Buguei 😅",
                "Dei tela azul 😂",
                "Pera aí 🤔"
            ])

        return resposta

    except Exception as e:
        logging.error(f"ERRO IA: {e}")
        return "Deu ruim aqui mas já volto 😎"


# ============== START ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Malu online!")

# ============== MENSAGENS ==================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    texto_original = msg.text.strip()
    texto = texto_original.lower()

    bot_username = context.bot.username.lower()

    # 🚫 não responder reply a humanos
    if msg.reply_to_message:
        autor = msg.reply_to_message.from_user
        if autor and not autor.is_bot:
            return

    # 🚫 não responder @alguem exceto bot
    if msg.entities:
        for ent in msg.entities:
            if ent.type == "mention":
                mencionado = texto_original[ent.offset: ent.offset + ent.length].lower()
                if mencionado != f"@{bot_username}":
                    return

    # respostas rápidas
    if texto in RESPOSTAS_RAPIDAS:
        await msg.reply_text(random.choice(RESPOSTAS_RAPIDAS[texto]))
        return

    # IA
    resposta = perguntar_ia(texto_original)
    await msg.reply_text(resposta)


# ============== MAIN ======================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("🤖 Bot rodando no Koyeb...")
    app.run_polling()


if __name__ == "__main__":
    main()
