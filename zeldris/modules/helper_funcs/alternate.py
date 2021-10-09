from functools import wraps

from telegram import error, ChatAction

from zeldris import LOGGER


def send_message(message, text, *args, **kwargs):
    try:
        return message.reply_text(text, *args, **kwargs)
    except error.BadRequest as err:
        if str(err) == "Reply message not found":
            return message.reply_text(text, quote=False, *args, **kwargs)
        raise


def typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        try:
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action=ChatAction.TYPING
            )
            return func(update, context, *args, **kwargs)
        except error.BadRequest as err:
            if str(err) == "Have no rights to send a message":
                LOGGER.warning("Bot muted in {} {}".format(
                        update.effective_message.chat.title,
                        update.effective_message.chat.id
                    )
                )
        except error.Unauthorized:
            return

    return command_func


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action=action
            )
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator
