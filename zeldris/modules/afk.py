#  ZeldrisRobot
#  Copyright (C) 2017-2019, Paul Larsen
#  Copyright (C) 2022, IDNCoderX Team, <https://github.com/IDN-C-X/ZeldrisRobot>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.


import time

from telegram import MessageEntity, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, MessageHandler

from zeldris import dispatcher, REDIS
from zeldris.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from zeldris.modules.helper_funcs.readable_time import get_readable_time
from zeldris.modules.redis.afk_redis import (
    start_afk,
    end_afk,
    is_user_afk,
    afk_reason,
)
from zeldris.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


def afk(update: Update, _: CallbackContext):
    message = update.effective_message
    args = message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [777000, 1087968824]:
        return

    start_afk_time = time.time()
    reason = args[1] if len(args) >= 2 else "none"
    start_afk(user.id, reason)
    REDIS.set(f"afk_time_{user.id}", start_afk_time)
    fname = user.first_name
    try:
        message.reply_text(
            f"<code>{fname}</code> is now AFK!", parse_mode=ParseMode.HTML
        )
    except BadRequest:
        pass


def no_longer_afk(update: Update, _: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    if not is_user_afk(user.id):  # Check if user is afk or not
        return

    x = REDIS.get(f"afk_time_{user.id}")
    if not x:
        return

    end_afk_time = get_readable_time((time.time() - float(x)))
    REDIS.delete(f"afk_time_{user.id}")
    res = end_afk(user.id)
    if res:
        if message.new_chat_members:  # don't say message
            return
        firstname = user.first_name
        try:
            message.reply_text(
                f"<b>{firstname}</b> is back online!\n"
                f"You were away for: <code>{end_afk_time}</code>",
                parse_mode=ParseMode.HTML,
            )
        except BadRequest:
            return


def reply_afk(update: Update, context: CallbackContext):
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(
                    message.text[ent.offset : ent.offset + ent.length]
                )
                if not user_id:
                    # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                    return

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

                try:
                    chat = context.bot.get_chat(user_id)
                except BadRequest as e:
                    print(
                        "Error: Could not fetch userid {} for AFK module due to {}".format(
                            user_id, e
                        )
                    )
                    return
                fst_name = chat.first_name

            else:
                return

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update: Update, _, user_id: int, fst_name: int, userc_id: int):
    message = update.effective_message
    if is_user_afk(user_id):
        reason = afk_reason(user_id)
        z = REDIS.get(f"afk_time_{user_id}")
        if not z:
            return

        since_afk = get_readable_time((time.time() - float(z)))
        if int(userc_id) == int(user_id):
            return
        if reason == "none":
            res = f"<b>{fst_name}</b> is AFK!\nLast seen: <code>{since_afk}</code>"
        else:
            res = f"<b>{fst_name}</b> is AFK!\nReason: {reason}\nLast seen: {since_afk}"

        message.reply_text(res, parse_mode=ParseMode.HTML)


def __gdpr__(user_id):
    end_afk(user_id)


__help__ = """
When marked as AFK, any mentions will be replied to with a message to say you're not available!

× /afk `<reason>`: Mark yourself as AFK.
× brb `<reason>`: Same as the afk command - but not a command.

An example of how to afk or brb:
`/afk dinner` or brb dinner.
"""

AFK_HANDLER = DisableAbleCommandHandler(
    "afk",
    afk,
    run_async=True,
)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(
    Filters.regex("(?i)^brb"),
    afk,
    friendly="afk",
    run_async=True,
)
NO_AFK_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups,
    no_longer_afk,
    run_async=True,
)
AFK_REPLY_HANDLER = MessageHandler(
    Filters.all & Filters.chat_type.groups & ~Filters.update.edited_message,
    reply_afk,
    run_async=True,
)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__mod_name__ = "AFK"
__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (AFK_REGEX_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]
