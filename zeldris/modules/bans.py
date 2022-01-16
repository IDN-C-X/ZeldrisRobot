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


import html
from typing import Optional

from telegram import Chat, Message, User, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import mention_html

from zeldris import dispatcher, LOGGER
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.admin_rights import user_can_ban
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.chat_status import (
    bot_admin,
    user_admin,
    is_user_ban_protected,
    can_restrict,
    is_user_admin,
    is_user_in_chat,
    can_delete,
)
from zeldris.modules.helper_funcs.extraction import extract_user_and_text
from zeldris.modules.helper_funcs.string_handling import extract_time
from zeldris.modules.log_channel import loggable


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def ban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.ban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            message.reply_text(
                f"Banned channel <b>{html.escape(message.reply_to_message.sender_chat.title)}</b> "
                f"from <b>{html.escape(chat.title)}</b>\n\n💡 He can only write with his profile "
                f"but not through other channels.",
                parse_mode=ParseMode.HTML,
            )
        else:
            message.reply_text("Failed to ban channel")
        return

    if user_can_ban(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to ban users!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude at least refer some user to ban!")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I'm not gonna ban an admin, don't make fun of yourself!")
        return ""

    if message.text.startswith("/d") and message.reply_to_message:
        message.reply_to_message.delete()

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy or wot?")
        return ""

    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False

    log = (
        "<b>{}:</b>"
        "\n#{}BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            "S" if silent else "",
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    reply = (
        f"Let {mention_html(member.user.id, member.user.first_name)} walk the plank.\n"
    )
    if reason:
        reply += f"<b>Reason:</b> {html.escape(reason)}"
    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            reply,
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("Banned!", quote=False)
            return log
        LOGGER.warning(update)
        LOGGER.exception(
            "ERROR banning user %s in chat %s (%s) due to %s",
            user_id,
            chat.title,
            chat.id,
            excp.message,
        )
        message.reply_text("Well damn, I can't ban that user.")

    return ""


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def temp_ban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_ban(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to temporarily ban someone!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude! at least refer some user to ban...")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Wow! let's start banning Admins themselves?...")
        return ""

    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy or wot?")
        return ""

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return ""

    log = (
        "<b>{}:</b>"
        "\n#TEMP BANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)"
        "\n<b>Time:</b> {}".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
            time_val,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    reply = f"Banned! User will be banned for {time_val}.\n"
    if reason:
        reply += f"<b>Reason:</b> {html.escape(reason)}"
    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            reply,
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                "Goodbye.. we'll meet after {}.".format(time_val), quote=False
            )
            return log
        LOGGER.warning(update)
        LOGGER.exception(
            "ERROR banning user %s in chat %s (%s) due to %s",
            user_id,
            chat.title,
            chat.id,
            excp.message,
        )
        message.reply_text("Well damn, I can't ban that user.")

    return ""


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def kick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    if user_can_ban(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to kick users!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude! at least refer some user to kick...")
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""
    if is_user_ban_protected(chat, user_id):
        message.reply_text("Yeahh... let's start kicking admins?")
        return ""

    if user_id == context.bot.id:
        message.reply_text("Yeahhh I'm not gonna do that")
        return ""

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        context.bot.sendMessage(
            chat.id,
            "Untill we meet again {}!.".format(
                mention_html(member.user.id, member.user.first_name)
            ),
            parse_mode=ParseMode.HTML,
        )
        log = (
            "<b>{}:</b>"
            "\n#KICKED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {} (<code>{}</code>)".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(member.user.id, member.user.first_name),
                member.user.id,
            )
        )
        if reason:
            log += "\n<b>Reason:</b> {}".format(reason)

        return log
    message.reply_text("Get Out!.")

    return ""


@bot_admin
@can_restrict
@loggable
@typing_action
def banme(update: Update, _: CallbackContext):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna ban an admin.")
        return

    res = update.effective_chat.ban_member(user_id)
    if res:
        update.effective_message.reply_text("Yes, you're right! GTFO..")
        return (
            "<b>{}:</b>"
            "\n#BANME"
            "\n<b>User:</b> {}"
            "\n<b>ID:</b> <code>{}</code>".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                user_id,
            )
        )
    update.effective_message.reply_text("Huh? I can't :/")


@bot_admin
@can_restrict
@typing_action
def kickme(update: Update, _: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna kick an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("Yeah, you're right Get Out!..")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@bot_admin
@can_restrict
@user_admin
@loggable
@typing_action
def unban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.unban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            message.reply_text(
                f"Unbanned channel <b>{html.escape(message.reply_to_message.sender_chat.title)}</b> "
                f"from <b>{html.escape(chat.title)}</b>\n\n💡 Now this users can send the messages "
                f"with they channel again",
                parse_mode=ParseMode.HTML,
            )
        else:
            message.reply_text("Failed to unban channel")
        return
    if user_can_ban(chat, user, context.bot.id) is False:
        message.reply_text("You don't have enough rights to unban people here!")
        return ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user")
        return ""
    if user_id == context.bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return ""

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "Why are you trying to unban someone who's already in this chat?"
        )
        return ""

    chat.unban_member(user_id)
    message.reply_text("Done, they can join again!")

    log = (
        "<b>{}:</b>"
        "\n#UNBANNED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {} (<code>{}</code>)".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(member.user.id, member.user.first_name),
            member.user.id,
        )
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    return log


__help__ = """
Some people need to be publicly banned; spammers, annoyances, or just trolls.
This module allows you to do that easily, by exposing some common actions, so everyone will see!

× /kickme: Kicks the user who issued the command.
× /banme: Bans the user who issued the command.

*Admin only:*
× /ban `<userhandle>`: Bans a user. (via handle, or reply).
× /sban `<userhandle>`: Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply).
× /dban: Bans a user and delete the message. (via handle, or reply).
× /tban `<userhandle> x(m/h/d)`: Bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days.
× /unban `<userhandle>`: Unbans a user. (via handle, or reply).
× /kick `<userhandle>`: Kicks a user, (via handle, or reply).

An example of temporarily banning someone:
`/tban @username 2h`; this bans a user for 2 hours.
"""

__mod_name__ = "Bans"

BAN_HANDLER = CommandHandler(
    ["ban", "dban", "sban"],
    ban,
    pass_args=True,
    filters=Filters.chat_type.groups,
    run_async=True,
)
TEMPBAN_HANDLER = CommandHandler(
    ["tban", "tempban"],
    temp_ban,
    pass_args=True,
    filters=Filters.chat_type.groups,
    run_async=True,
)
KICK_HANDLER = CommandHandler(
    "kick", kick, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
UNBAN_HANDLER = CommandHandler(
    "unban", unban, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.chat_type.groups, run_async=True
)
BANME_HANDLER = DisableAbleCommandHandler(
    "banme", banme, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(BANME_HANDLER)
