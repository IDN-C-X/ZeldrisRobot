# Copyright (C) 2017-2019, Paul Larsen
# Copyright (c) 2019-2021, corsicanu
# Copyright (c) 2020-2021, soulr344
# Copyright (c) 2021, IDNCoderX
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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
