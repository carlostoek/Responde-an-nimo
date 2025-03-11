import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

# 🔑 Configuración del bot
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))  # Usa un valor por defecto si la variable no está definida

# 🚀 Configurar el bot y el Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📩 Manejar mensajes de usuarios
@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.reply("¡Hola! Envía tu pregunta de forma anónima.")

@dp.message_handler()
async def recibir_pregunta(message: Message):
    if message.chat.type == "private":  # Asegura que solo reciba en chats privados
        pregunta = message.text

        # Enviar la pregunta al administrador
        pregunta_enviada = await bot.send_message(ADMIN_ID, f"📩 Nueva Pregunta Anónima:\n{pregunta}")

        # Guardar el ID del mensaje para poder usarlo más tarde
        # Esto es necesario para que el bot sepa a qué pregunta está respondiendo el administrador
        message_id = pregunta_enviada.message_id

        # Agregar la información al mensaje del usuario
        await message.reply("✅ Tu pregunta ha sido enviada de forma anónima. El administrador responderá pronto.")

# 🚀 Función para manejar la respuesta del administrador
@dp.message_handler(lambda message: message.reply_to_message and message.reply_to_message.from_user.id == ADMIN_ID)
async def responder_pregunta(message: Message):
    # Verificamos que el mensaje sea una respuesta a una pregunta enviada por el bot al administrador
    if message.reply_to_message:
        original_message = message.reply_to_message
        if original_message.text:
            user_id = original_message.forward_from.id  # ID del usuario que hizo la pregunta
            pregunta = original_message.text

            # Reenviar la respuesta del administrador al usuario original
            await bot.send_message(user_id, f"📝 Respuesta a tu pregunta: {message.text}")

            # Notificar al administrador que la respuesta fue enviada
            await message.reply("✅ Respuesta enviada al usuario.")

# 🔄 Iniciar el bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
