import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

# Configuración
TOKEN = "TU_TOKEN_AQUI"  # Reemplázalo con el token de tu bot
ADMIN_ID = TU_ID_AQUI  # Tu ID de usuario en Telegram

# Inicializar bot y dispatcher
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Comando /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hola, envíame cualquier pregunta y la haré llegar de forma anónima.")

# Captura cualquier mensaje y lo reenvía al admin
@dp.message()
async def receive_question(message: Message):
    user_id = message.from_user.id
    question = message.text

    # Enviar pregunta al administrador
    admin_message = f"📩 Nueva pregunta anónima:\n\n{question}"
    await bot.send_message(ADMIN_ID, admin_message)

    # Responder al usuario confirmando la recepción
    await message.answer("✅ Tu pregunta ha sido enviada de forma anónima.")

# Iniciar el bot
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
