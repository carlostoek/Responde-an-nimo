import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

# 🔑 Configuración del bot
TOKEN = "7742088459:AAEhHFvSjnxZkIsLi746Kv-XmTOy06y6DHU"
ADMIN_ID = 6181290784  # Tu ID de Telegram

# 🚀 Configurar el bot y el Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📩 Manejar mensajes de usuarios
@dp.message()
async def recibir_pregunta(message: Message):
    if message.chat.type == "private":  # Asegura que solo reciba en chats privados
        pregunta = message.text
        await bot.send_message(ADMIN_ID, f"📩 **Nueva Pregunta Anónima:**\n{pregunta}")
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima.")

# 🔄 Iniciar el bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
