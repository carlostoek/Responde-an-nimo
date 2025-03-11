import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# Obtén los valores desde las variables de entorno
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Diccionario para mapear el ID del mensaje enviado al admin con el ID del usuario que hizo la pregunta
pregunta_mapping = {}

# Handler para recibir preguntas de usuarios (excluyendo al admin)
@dp.message_handler(lambda message: message.chat.type == "private" and message.from_user.id != ADMIN_ID)
async def recibir_pregunta(message: Message):
    pregunta = message.text
    # Enviar la pregunta al administrador y obtener el mensaje enviado
    sent_message = await bot.send_message(
        ADMIN_ID,
        f"📩 Nueva Pregunta Anónima:\n{pregunta}"
    )
    # Almacenar en el diccionario el ID del mensaje del admin y el ID del usuario que hizo la pregunta
    pregunta_mapping[sent_message.message_id] = message.from_user.id
    await message.reply("✅ Tu pregunta ha sido enviada de forma anónima. El administrador responderá pronto.")

# Handler para que el administrador responda (usando la función de "responder" de Telegram)
@dp.message_handler(lambda message: message.chat.type == "private" 
                                  and message.from_user.id == ADMIN_ID 
                                  and message.reply_to_message is not None)
async def responder_pregunta(message: Message):
    # Obtén el ID del mensaje al que se está respondiendo (el mensaje que el bot envió al admin)
    admin_msg_id = message.reply_to_message.message_id
    if admin_msg_id in pregunta_mapping:
        user_id = pregunta_mapping[admin_msg_id]
        # Enviar la respuesta del administrador al usuario correspondiente
        await bot.send_message(
            user_id,
            f"📝 Respuesta del Administrador:\n{message.text}"
        )
        await message.reply("✅ Respuesta enviada al usuario.")
        # Eliminar la entrada del diccionario para evitar duplicados
        del pregunta_mapping[admin_msg_id]
    else:
        await message.reply("❌ No se encontró la pregunta asociada a esta respuesta.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
