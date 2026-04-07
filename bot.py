import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Configurações (usa variáveis de ambiente)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Configurar Groq
client = Groq(api_key=GROQ_API_KEY)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    await update.message.reply_text("🤖 Bot ativo com Llama 3.3! Use /ajuda")

async def ajuda(update: Update, context):
    await update.message.reply_text("""
🤖 COMANDOS:
/ia [pergunta] - IA (Llama 3.3 70B)
/ban - Banir usuário
/status - Ver status
/regras - Ver regras
    """)

async def ia_comando(update: Update, context):
    if not context.args:
        await update.message.reply_text("Use: /ia sua pergunta")
        return
    pergunta = ' '.join(context.args)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": pergunta}],
            max_tokens=500,
            temperature=0.7
        )
        await update.message.reply_text(f"🤖 {response.choices[0].message.content}")
    except Exception as e:
        await update.message.reply_text(f"Erro: {str(e)[:200]}")

async def ban_comando(update: Update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("Responda a mensagem!")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("🔨 Banido!")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

async def status_comando(update: Update, context):
    await update.message.reply_text("✅ Online 24/7 com Llama 3.3 70B!")

async def regras_comando(update: Update, context):
    await update.message.reply_text("📜 Respeite todos. Sem spam.")

async def boas_vindas(update: Update, context):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Bem-vindo {member.first_name}!")

async def responder_mencao(update: Update, context):
    if not update.message or not update.message.text:
        return
    bot_mencionado = f"@{context.bot.username}" in update.message.text
    if bot_mencionado or (update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id):
        texto = update.message.text.replace(f"@{context.bot.username}", "").strip()
        if texto:
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": texto}],
                    max_tokens=500,
                    temperature=0.7
                )
                await update.message.reply_text(f"🤖 {response.choices[0].message.content}")
            except:
                pass

def main():
    logger.info("🤖 Iniciando bot 24/7...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("ia", ia_comando))
    app.add_handler(CommandHandler("ban", ban_comando))
    app.add_handler(CommandHandler("status", status_comando))
    app.add_handler(CommandHandler("regras", regras_comando))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, boas_vindas))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mencao))
    
    logger.info("✅ Bot online!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
