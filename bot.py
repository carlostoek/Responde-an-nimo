from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os

TOKEN = "TU_BOT_TOKEN_AQUI"
GROUP_ID = -1001234567890  # ID del grupo donde se publican las preguntas

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Diccionario temporal para almacenar preguntas y sus autores
preguntas_pendientes = {}

# Enviar pregunta de forma anónima
@dp.message_handler(commands=['preguntar'])
async def handle_preguntar(message: types.Message):
    await message.answer("Envía tu pregunta de forma anónima:")
    dp.register_message_handler(capturar_pregunta, state=None)

async def capturar_pregunta(message: types.Message):
    pregunta = message.text
    user_id = message.from_user.id
    mensaje_publicado = await bot.send_message(
        GROUP_ID,
        f"📩 **Nueva pregunta anónima:**\n\n❓ {pregunta}",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Responder", callback_data=f"responder_{user_id}")
        )
    )
    preguntas_pendientes[mensaje_publicado.message_id] = user_id

# Responder pregunta (solo admins)
@dp.callback_query_handler(lambda c: c.data.startswith("responder_"))
async def handle_responder(callback_query: types.CallbackQuery):
    admin_list = [admin.user.id for admin in await bot.get_chat_administrators(GROUP_ID)]
    if callback_query.from_user.id not in admin_list:
        await callback_query.answer("Solo los administradores pueden responder.", show_alert=True)
        return

    user_id = int(callback_query.data.split("_")[1])
    await bot.send_message(callback_query.from_user.id, "Escribe tu respuesta para el usuario:")
    dp.register_message_handler(lambda msg: enviar_respuesta(msg, user_id), state=None)

async def enviar_respuesta(message: types.Message, user_id: int):
    respuesta = message.text
    await bot.send_message(user_id, f"📩 **Respuesta a tu pregunta anónima:**\n\n💬 {respuesta}")
    await message.answer("✅ Respuesta enviada de forma anónima.")

# Iniciar bot
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
