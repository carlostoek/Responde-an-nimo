from telegram import Update
from telegram.ext import Application, MessageHandler, filters
import os

# Obtén los valores desde las variables de entorno (Railway)
TOKEN = os.getenv("7742088459:AAEhHFvSjnxZkIsLi746Kv-XmTOy06y6DHU")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))  # Usa un valor por defecto si la variable no está definida

# Inicializa la aplicación de Telegram
app = Application.builder().token(TOKEN).build()

async def forward_to_admin(update: Update, context):
    """Reenvía cualquier mensaje recibido al administrador"""
    user = update.message.from_user
    text = f"📩 Nueva pregunta de @{user.username or user.first_name}:\n\n{update.message.text}"
    
    # Enviar el mensaje al administrador
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)

# Manejar cualquier mensaje recibido
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))

# Iniciar el bot
if __name__ == "__main__":
    print("🤖 Bot en ejecución...")
    app.run_polling()
