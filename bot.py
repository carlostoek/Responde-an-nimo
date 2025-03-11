import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# Obtén los valores desde las variables de entorno (Railway)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))  # Usa un valor por defecto si la variable no está definida

# Configuración del bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Diccionario para almacenar las preguntas y el usuario que las envió
preguntas = {}

# Manejar las preguntas de los usuarios
@dp.message_handler()
async def recibir_pregunta(message: types.Message):
    # Asegurarnos de que solo se reciban preguntas de los usuarios (no del administrador)
    if message.chat.type == "private" and message.from_user.id != ADMIN_ID:
        pregunta = message.text
        # Guardamos la pregunta y el ID del usuario
        preguntas[message.message_id] = message.from_user.id
        await bot.send_message(ADMIN_ID, f"📩 Nueva Pregunta Anónima:\n{pregunta}\n\nResponde en privado.")
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima. El administrador responderá pronto.")

# Manejar las respuestas del administrador
@dp.message_handler()
async def responder_a_pregunta(message: types.Message):
    # Asegurarnos de que solo el administrador pueda responder preguntas
    if message.chat.type == "private" and message.from_user.id == ADMIN_ID:
        # Verificar si el mensaje es una respuesta a una pregunta
        if message.reply_to_message and message.reply_to_message.forward_from:
            user_id = preguntas.get(message.reply_to_message.message_id)  # Obtener el ID del usuario que hizo la pregunta
            if user_id:
                await bot.send_message(user_id, f"✅ Respuesta del Administrador:\n{message.text}", parse_mode=ParseMode.MARKDOWN)
                await message.reply("✅ Respuesta enviada al usuario correctamente.")
                # Eliminar la pregunta del diccionario para evitar confusión con futuras respuestas
                del preguntas[message.reply_to_message.message_id]
        else:
            await message.reply("❌ No hay ninguna pregunta a la que responder.")
    else:
        # Evitar que los mensajes del administrador se procesen como preguntas anónimas
        await message.reply("❌ No puedes hacer preguntas en este chat.")

# Iniciar el bot
async def on_start():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(on_start())
