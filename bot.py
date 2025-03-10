from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio

# 🔑 Configuración del bot
TOKEN = "7742088459:AAEhHFvSjnxZkIsLi746Kv-XmTOy06y6DHU"
ADMIN_ID = 6181290784  # Tu ID de Telegram

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📩 Manejar mensajes de usuarios
@dp.message_handler()
async def recibir_pregunta(message: types.Message):
    if message.chat.type == "private":  # Asegura que solo reciba en chats privados
        pregunta = message.text
        await bot.send_message(ADMIN_ID, f"📩 **Nueva Pregunta Anónima:**\n{pregunta}")
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima.")

# 🔄 Iniciar el bot
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
