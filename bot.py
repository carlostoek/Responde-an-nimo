import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery

# 🔑 Configuración del bot usando variables de entorno
TOKEN = os.getenv("BOT_TOKEN")  # Obtén el token del bot desde la variable de entorno
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))  # Obtén el ID del administrador desde la variable de entorno

# 🚀 Configurar el bot y el Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)  # Aquí pasamos el bot al Dispatcher

# 💬 Crear un sistema de datos para almacenar la pregunta y el ID del usuario
question_data = {}

# 📩 Manejar mensajes de usuarios
@dp.message()
async def recibir_pregunta(message: Message):
    if message.chat.type == "private":  # Asegura que solo reciba en chats privados
        pregunta = message.text
        user_id = message.from_user.id
        # Almacenar la pregunta y el ID del usuario
        question_data[user_id] = pregunta
        # Enviar la pregunta al administrador
        await bot.send_message(ADMIN_ID, f"📩 Nueva Pregunta Anónima:\n{pregunta}\n\n"
                                        f"📝 Responder esta pregunta en privado.")
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima.")

# 🔘 Manejar el botón para responder en privado
@dp.callback_query_handler(lambda c: c.data == 'responder_pregunta')
async def responder_pregunta(callback_query: CallbackQuery):
    # El ID del usuario que hizo la pregunta está almacenado en 'question_data'
    user_id = callback_query.from_user.id
    if user_id in question_data:
        pregunta = question_data[user_id]
        # Enviar la respuesta en privado al usuario
        await bot.send_message(user_id, f"📩 Respuesta a tu pregunta: {pregunta}\n\n"
                                        "Aquí está la respuesta del administrador.")
        # Confirmar que se ha enviado la respuesta
        await bot.answer_callback_query(callback_query.id, text="Respuesta enviada en privado.")
    else:
        await bot.answer_callback_query(callback_query.id, text="No se encontró la pregunta correspondiente.")

# 🔄 Iniciar el bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
