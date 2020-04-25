import html, time
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User
from telegram.error import BadRequest
from telegram.ext import Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from skylee import dispatcher, LOGGER
from skylee.modules.disable import DisableAbleCommandHandler
from skylee.modules.helper_funcs.chat_status import user_admin, can_delete
from skylee.modules.helper_funcs.admin_rights import user_can_delete
from skylee.modules.log_channel import loggable


@run_async
@user_admin
@loggable
def purge(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]
    if msg.reply_to_message:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        if user_can_delete(chat, user, context.bot.id) == False:
           msg.reply_text("You don't have enough rights to delete message!")
           return ""
        if can_delete(chat, context.bot.id):
            message_id = msg.reply_to_message.message_id
            delete_to = msg.message_id - 1
            if args and args[0].isdigit():
                new_del = message_id + int(args[0])
                # No point deleting messages which haven't been written yet.
                if new_del < delete_to:
                    delete_to = new_del

            for m_id in range(delete_to, message_id - 1, -1):  # Reverse iteration over message ids
                try:
                    context.bot.deleteMessage(chat.id, m_id)
                except BadRequest as err:
                    if err.message == "Message can't be deleted":
                        context.bot.send_message(chat.id, "Cannot delete all messages. The messages may be too old, I might "
                                                  "not have delete rights, or this might not be a supergroup.")

                    elif err.message != "Message to delete not found":
                        LOGGER.exception("Error while purging chat messages.")

            try:
                msg.delete()
            except BadRequest as err:
                if err.message == "Message can't be deleted":
                    context.bot.send_message(chat.id, "Cannot delete all messages. The messages may be too old, I might "
                                              "not have delete rights, or this might not be a supergroup.")

                elif err.message != "Message to delete not found":
                    LOGGER.exception("Error while purging chat messages.")

            del_msg = context.bot.send_message(chat.id, "Purge complete.")
            time.sleep(2)

            try:
                del_msg.delete()

            except BadRequest:
                pass

            return "<b>{}:</b>" \
                   "\n#PURGE" \
                   "\n<b>Admin:</b> {}" \
                   "\nPurged <code>{}</code> messages.".format(html.escape(chat.title),
                                                               mention_html(user.id, user.first_name),
                                                               delete_to - message_id)

    else:
        msg.reply_text("Reply to a message to select where to start purging from.")

    return ""


@run_async
@user_admin
@loggable
def del_message(update, context) -> str:
    if update.effective_message.reply_to_message:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        message = update.effective_message  # type: Optional[Message]
        if user_can_delete(chat, user, context.bot.id) == False:
           message.reply_text("You don't have enough rights to delete message!")
           return ""
        if can_delete(chat, context.bot.id):
            update.effective_message.reply_to_message.delete()
            update.effective_message.delete()
            return "<b>{}:</b>" \
                   "\n#DEL" \
                   "\n<b>Admin:</b> {}" \
                   "\nMessage deleted.".format(html.escape(chat.title),
                                               mention_html(user.id, user.first_name))
    else:
        update.effective_message.reply_text("Whadya want to delete?")

    return ""


__help__ = """
Deleting messages made easy with this command. Bot purges \
messages all together or individually.

*Admin only:*
 - /del: Deletes the message you replied to
 - /purge: Deletes all messages between this and the replied to message.
 - /purge <integer X>: Deletes the replied message, and X messages following it.
"""

__mod_name__ = "Purges"

DELETE_HANDLER = DisableAbleCommandHandler("del", del_message, filters=Filters.group)
PURGE_HANDLER = DisableAbleCommandHandler("purge", purge, filters=Filters.group, pass_args=True)

dispatcher.add_handler(DELETE_HANDLER)
dispatcher.add_handler(PURGE_HANDLER)
