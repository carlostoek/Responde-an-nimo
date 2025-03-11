import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os

# Obtén los valores desde las variables de entorno (Railway)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))  # Usa un valor por defecto si la variable no está definida

# Configurar el bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Mensaje de bienvenida para usuarios
async def send_welcome(message: Message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Enviar pregunta de forma anónima", callback_data="ask_question")
    markup.add(button)
    await message.reply("¡Bienvenido al Bot de Preguntas Anónimas! 😊\nHaz tu pregunta y será enviada al administrador de forma anónima.", reply_markup=markup)

# Manejar el comando /start
@dp.message_handler(commands=['start'])
async def start(message: Message):
    await send_welcome(message)

# Manejar preguntas anónimas de los usuarios
@dp.message_handler(content_types=types.ContentType.TEXT)
async def recibir_pregunta(message: Message):
    if message.chat.type == "private":  # Solo procesamos mensajes en privado
        pregunta = message.text
        await bot.send_message(ADMIN_ID, f"📩 **Nueva Pregunta Anónima**:\n{pregunta}\n\nPara responder, toca el botón de abajo. ¡Gracias!", reply_markup=inline_reply_markup(message.message_id))
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima.")

# Crear los botones para que el administrador responda
def inline_reply_markup(message_id: int):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Responder en privado", callback_data=f"respond_{message_id}")
    markup.add(button)
    return markup

# Gestionar la respuesta del administrador
@dp.callback_query_handler(lambda c: c.data.startswith('respond_'))
async def handle_response(callback_query: types.CallbackQuery):
    message_id = int(callback_query.data.split("_")[1])  # Extraemos el message_id
    original_message = await bot.get_message(ADMIN_ID, message_id)  # Obtenemos el mensaje original
    user_id = original_message.from_user.id  # Extraemos el ID del usuario que hizo la pregunta

    await bot.send_message(user_id, "🔔 Tienes una respuesta del administrador:\n\n" + callback_query.message.text)
    await callback_query.answer("¡Respuesta enviada al usuario!")

    # El administrador también puede ver un mensaje de confirmación
    await bot.send_message(ADMIN_ID, "✔️ Respuesta enviada correctamente al usuario.")

# Iniciar el bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
