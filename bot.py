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
# >>> Variable de entorno para el ID del canal VIP <<<
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) # Asegúrate de que esta variable esté configurada en Railway

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Diccionario para mapear el ID del mensaje enviado al admin con el ID del usuario que hizo la pregunta
# {admin_msg_id: user_id}
pregunta_mapping = {}

# Handler para recibir preguntas de usuarios (excluyendo al admin, el comando /start y otros comandos)
@dp.message_handler(lambda message: message.chat.type == "private" and message.from_user.id != ADMIN_ID and message.text != "/start" and not message.text.startswith('/'))
async def recibir_pregunta(message: Message):
    user_id = message.from_user.id
    channel_id = CHANNEL_ID

    # --- Paso 1: Verificar Membresía ---
    try:
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        status = chat_member.status

        if status not in ['creator', 'administrator', 'member']:
            await message.reply("⛔️ Lo siento, no estás registrado para usar este bot.")
            return # Salir del handler si no es miembro

    except ChatNotFound:
        logging.error(f"El bot no puede encontrar el canal con ID {channel_id}. ¿Está configurado correctamente y el bot es miembro?")
        await message.reply("❌ Ha ocurrido un error interno al verificar el canal. Por favor, informa al administrador.")
        return # Salir si no se encuentra el canal

    except Exception as e:
        # Capturar cualquier otro error durante la verificación de membresía
        logging.error(f"Error inesperado al verificar membresía del usuario {user_id}: {e}")
        await message.reply("❌ Ha ocurrido un error al verificar tu estado. Por favor, intenta más tarde.")
        return # Salir si ocurre otro error en la verificación


    # --- Paso 2: Si es miembro, enviar mensaje al admin ---
    # Este bloque solo se ejecuta si la verificación de membresía fue exitosa
    try:
        pregunta = message.text
        sent_message = await bot.send_message(
            ADMIN_ID,
            f"📩 **Nueva Pregunta Anónima**:\n\n{pregunta}\n\n*Procesando ID...*" # Enviamos un mensaje inicial sin el ID definitivo
        )
        # Una vez enviado, obtenemos su ID
        admin_msg_id = sent_message.message_id

        # Ahora editamos el mensaje para incluir su propio ID (el ID del mensaje que el bot envió al admin)
        await bot.edit_message_text(
             chat_id=ADMIN_ID,
             message_id=admin_msg_id,
             text=f"📩 **Nueva Pregunta Anónima**:\n\n{pregunta}\n\n*ID Mensaje Bot (para revelar identidad):* `{admin_msg_id}`\n\nPara responder, toca la opción de abajo. ¡Gracias! 👇",
             parse_mode='Markdown'
        )

        # Almacenar en el diccionario {ID_mensaje_bot_a_admin : ID_usuario_original}
        pregunta_mapping[admin_msg_id] = user_id


        # Confirmar al usuario
        await message.reply("✅ ¡Tu pregunta ha sido enviada de forma anónima! El administrador te responderá pronto. 🙏")

    except Exception as e:
        # Capturar errores durante el envío o edición del mensaje al admin o al actualizar el mapping
        # En este punto, la membresía ya fue verificada.
        logging.error(f"Error al enviar/editar mensaje al admin o actualizar mapping para user {user_id}: {e}")
        await message.reply("❌ Ha ocurrido un error al procesar o enviar tu pregunta. Por favor, informa al administrador.")
        # No salimos con return aquí para que el primer reply al usuario (si se ejecutó antes del error) no se pierda,
        # aunque si el error ocurre *antes* del primer reply, el usuario podría no recibir confirmación ni error.
        # La confirmación al usuario está ahora DESPUÉS del envío y edición al admin, así que si falla antes, no la recibe.
        # Esto es mejor: solo confirma si la operación al admin fue exitosa.


# Handler para que el administrador responda (usando la función de "responder" de Telegram)
# No necesita cambios
@dp.message_handler(lambda message: message.chat.type == "private"
                                  and message.from_user.id == ADMIN_ID
                                  and message.reply_to_message is not None)
async def responder_pregunta(message: Message):
    # Obtén el ID del mensaje al que se está respondiendo (el mensaje que el bot envió al admin)
    admin_msg_id = message.reply_to_message.message_id

    if admin_msg_id in pregunta_mapping:
        user_id = pregunta_mapping[admin_msg_id] # Obtenemos el ID del usuario original
        # Enviar la respuesta del administrador al usuario correspondiente
        try:
            await bot.send_message(
                user_id,
                f"📝 **Respuesta del Administrador**:\n\n{message.text}\n\n¡Gracias por tu paciencia! 😎"
            )
            await message.reply("✅ ¡Tu respuesta ha sido enviada al usuario con éxito! ✨")
            # Eliminar la entrada del diccionario para evitar que crezca indefinidamente
            del pregunta_mapping[admin_msg_id]
        except Exception as e:
             logging.error(f"Error al enviar respuesta a user {user_id} para admin_msg {admin_msg_id}: {e}")
             await message.reply("❌ **Error**: No se pudo enviar la respuesta al usuario. 🤔")
    else:
        await message.reply("❌ **Error**: No se encontró la pregunta asociada a esta respuesta o ya fue respondida. 🤔")


# >>> HANDLER PARA REVELAR ID <<<
# No necesita cambios en su lógica interna de búsqueda
@dp.message_handler(commands=['revelar_id'])
async def revelar_id(message: types.Message):
    # Solo permitir que el ADMIN_ID use este comando
    if message.from_user.id == ADMIN_ID:
        try:
            # Extraer el ID del mensaje *enviado al admin* de los argumentos del comando
            args = message.get_args().split()
            if not args:
                await message.reply("Uso: `/revelar_id <ID del mensaje que el bot te envió>`")
                return

            admin_msg_id_a_revelar = int(args[0])

            # Buscar el ID del usuario en el diccionario usando el ID del mensaje que el bot envió al admin
            user_id = pregunta_mapping.get(admin_msg_id_a_revelar)

            if user_id:
                # >>> Obtener información del usuario <<<
                try:
                    chat = await bot.get_chat(user_id) # Usamos get_chat con el user_id para obtener info del usuario
                    username = chat.username # Obtener el nombre de usuario (si lo tiene)
                    first_name = chat.first_name # Obtener el nombre
                    last_name = chat.last_name # Obtener el apellido
                    full_name = f"{first_name} {last_name}" if last_name else first_name # Combinar nombre y apellido si existe

                    respuesta = (
                        f"👤 **Información del Usuario** (Pregunta asociada al mensaje del admin ID `{admin_msg_id_a_revelar}`):\n\n"
                    )
                    if username:
                        respuesta += f"**Nombre de usuario:** @{username}\n"
                    respuesta += f"**Nombre completo:** {full_name}\n"
                    respuesta += f"**ID de usuario:** `{user_id}`" # Mostrar ID del usuario en formato code

                    await message.reply(respuesta, parse_mode='Markdown')
                except Exception as e:
                    logging.error(f"Error al obtener info del usuario {user_id} para revelar ID: {e}")
                    await message.reply(f"Se encontró el usuario (ID: `{user_id}`) pero ocurrió un error al obtener su información completa.")

            else:
                await message.reply(f"No se encontró el ID del usuario asociado al mensaje del admin ID `{admin_msg_id_a_revelar}` en el registro activo. La pregunta podría haber sido respondida ya o el ID es incorrecto.")

        except ValueError:
            await message.reply("Uso incorrecto. Uso: `/revelar_id <ID del mensaje que el bot te envió>`")
        except Exception as e:
            logging.error(f"Error general en handler revelar_id: {e}")
            await message.reply("Ocurrió un error al procesar tu solicitud.")
    else:
        # Si alguien que no es el admin intenta usar el comando
        await message.reply("No tienes permiso para usar este comando.")


# >>> HANDLER PARA EL COMANDO /help <<<
# No necesita cambios
@dp.message_handler(commands=['help'])
async def admin_help(message: types.Message):
    # Solo permitir que el ADMIN_ID use este comando
    if message.from_user.id == ADMIN_ID:
        help_text = (
            "📚 **Comandos y Funcionalidades del Administrador:**\n\n"
            "✅ **Responder a un usuario:**\n"
            "   Simplemente **responde al mensaje** de la pregunta que el bot te envió (usando la función 'Responder' de Telegram). Tu respuesta será enviada anónimamente al usuario original.\n\n"
            "🕵️ **Revelar identidad:**\n"
            "   Usa el comando `/revelar_id <ID del mensaje>`.\n"
            "   Donde `<ID del mensaje>` es el número `ID Mensaje Bot` que aparece en el mensaje de la pregunta que el bot te envió. Esto revelará el nombre de usuario, nombre completo y ID del usuario que envió esa pregunta.\n\n"
            "❓ **Ayuda:**\n"
            "   Usa el comando `/help` para mostrar este menú.\n\n"
            "*(Estos comandos solo funcionan en el chat privado con el bot)*"
        )
        await message.reply(help_text, parse_mode='Markdown')
    else:
        # Si un usuario normal usa /help
         await message.reply("No tienes comandos de administrador disponibles.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
