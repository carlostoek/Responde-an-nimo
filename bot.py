import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram import executor

# Configuración del bot
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# Inicializar bot y dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Manejar el inicio del bot
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("¡Hola! Envía tu pregunta de forma anónima y el administrador responderá en privado.")

# Recibir las preguntas de los usuarios
@dp.message_handler()
async def recibir_pregunta(message: types.Message):
    if message.chat.type == "private" and message.from_user.id != ADMIN_ID:
        pregunta = message.text
        # Enviar la pregunta al administrador
        await bot.send_message(ADMIN_ID, f"📩 Nueva Pregunta Anónima:\n{pregunta}",
                               reply_markup=types.ReplyKeyboardRemove())
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima. El administrador responderá pronto.")

# Responder a las preguntas como administrador
@dp.message_handler()
async def responder_a_pregunta(message: types.Message):
    if message.chat.type == "private" and message.from_user.id == ADMIN_ID:
        # Comprobar si el mensaje es una respuesta a una pregunta anterior
        if message.reply_to_message and message.reply_to_message.forward_from:
            user_id = message.reply_to_message.forward_from.id
            # Enviar la respuesta del administrador al usuario
            await bot.send_message(user_id, f"✅ Respuesta del Administrador:\n{message.text}",
                                   parse_mode=ParseMode.MARKDOWN)

# Iniciar el bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
