import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound # Importar excepción específica

# Obtén los valores desde las variables de entorno
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
# >>> AÑADIR ESTA LÍNEA PARA OBTENER EL ID DEL CANAL <<<
# Es CRUCIAL que esta variable de entorno esté definida en Railway
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) # Convertir a int


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Diccionario para mapear el ID del mensaje enviado al admin con el ID del usuario que hizo la pregunta
pregunta_mapping = {}

# Handler para recibir preguntas de usuarios (excluyendo al admin y el comando /start)
@dp.message_handler(lambda message: message.chat.type == "private" and message.from_user.id != ADMIN_ID and message.text != "/start")
async def recibir_pregunta(message: Message):
    user_id = message.from_user.id
    channel_id = CHANNEL_ID # Usamos el ID del canal configurado

    try:
        # >>> VERIFICAR MEMBRESÍA DEL USUARIO EN EL CANAL <<<
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        status = chat_member.status

        # Los estados 'creator', 'administrator' y 'member' indican que el usuario es miembro activo
        if status in ['creator', 'administrator', 'member']:
            # --- Lógica original para reenviar la pregunta (solo si es miembro) ---
            pregunta = message.text
            # Enviar la pregunta al administrador y obtener el mensaje enviado
            sent_message = await bot.send_message(
                ADMIN_ID,
                f"📩 **Nueva Pregunta Anónima**:\n\n{pregunta}\n\nPara responder, toca la opción de abajo. ¡Gracias! 👇"
            )
            # Almacenar en el diccionario el ID del mensaje del admin y el ID del usuario que hizo la pregunta
            pregunta_mapping[sent_message.message_id] = user_id
            await message.reply("✅ ¡Tu pregunta ha sido enviada de forma anónima! El administrador te responderá pronto. 🙏")
            # --- Fin de la lógica original ---
        else:
            # >>> EL USUARIO NO ES MIEMBRO DEL CANAL <<<
            # Enviarle un mensaje simple y no reenviar nada
            await message.reply("⛔️ Lo siento, no estás registrado para usar este bot.") # Mensaje simple sin sugerir registro

    except ChatNotFound:
        # Esto podría ocurrir si el CHANNEL_ID configurado es incorrecto o el bot no está en el canal.
        logging.error(f"El bot no puede encontrar el canal con ID {channel_id}. ¿Está configurado correctamente y el bot es miembro?")
        await message.reply("❌ Ha ocurrido un error interno al verificar el canal. Por favor, informa al administrador.")
    except Exception as e:
        # Capturar cualquier otro error durante la verificación
        logging.error(f"Error inesperado al verificar membresía del usuario {user_id} en el canal {channel_id}: {e}")
        await message.reply("❌ Ha ocurrido un error al verificar tu estado. Por favor, intenta más tarde.")


# Handler para que el administrador responda (usando la función de "responder" de Telegram)
# Este handler no necesita cambios, ya que solo lo usa el admin.
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
            f"📝 **Respuesta del Administrador**:\n\n{message.text}\n\n¡Gracias por tu paciencia! 😎"
        )
        await message.reply("✅ ¡Tu respuesta ha sido enviada al usuario con éxito! ✨")
        # Eliminar la entrada del diccionario para evitar duplicados
        del pregunta_mapping[admin_msg_id]
    else:
        await message.reply("❌ **Error**: No se encontró la pregunta asociada a esta respuesta. 🤔")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

