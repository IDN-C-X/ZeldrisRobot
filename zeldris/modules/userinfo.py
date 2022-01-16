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

from telegram import Message, User, Update
from telegram import ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

import zeldris.modules.sql.userinfo_sql as sql
from zeldris import dispatcher, DEV_USERS
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.extraction import extract_user


@typing_action
def about_me(update: Update, context: CallbackContext):
    message = update.effective_message  # type: Optional[Message]
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    user = bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            username + "Information about him is currently unavailable !"
        )
    else:
        update.effective_message.reply_text(
            "You have not added any information about yourself yet !"
        )


@typing_action
def set_about_me(update, _):
    message = update.effective_message
    user_id = message.from_user.id
    text = message.text
    info = text.split(
        None, 1
    )  # use python's maxsplit to only remove the cmd, hence keeping newlines.
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            message.reply_text("Your bio has been saved successfully")
        else:
            message.reply_text(
                " About You{} To be confined to letters ".format(
                    MAX_MESSAGE_LENGTH // 4, len(info[1])
                )
            )


@typing_action
def about_bio(update: Update, context: CallbackContext):
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    user_id = extract_user(message, args)
    user = context.bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            "{} No details about him have been saved yet !".format(username)
        )
    else:
        update.effective_message.reply_text(" Your bio  about you has been saved !")


@typing_action
def set_about_bio(update: Update, context: CallbackContext):
    message = update.effective_message  # type: Optional[Message]
    sender = update.effective_user  # type: Optional[User]
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id == message.from_user.id:
            message.reply_text("Are you looking to change your own ... ?? That 's it.")
            return
        if user_id == context.bot.id and sender.id not in DEV_USERS:
            message.reply_text(" Only my DEV USERS can change my information.")
            return

        text = message.text
        bio = text.split(
            None, 1
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.
        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text(
                    "{} bio has been successfully saved!".format(
                        repl_message.from_user.first_name
                    )
                )
            else:
                message.reply_text(
                    "About you {} Must stick to the letter! "
                    "The number of characters you have just tried {} hm .".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])
                    )
                )
    else:
        message.reply_text(" His bio can only be saved if someone MESSAGE as a REPLY")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return "<b>About user:</b>\n{me}\n\n<b>What others say:</b>\n{bio}".format(
            me=me, bio=bio
        )
    if bio:
        return "<b>What others say:</b>\n{bio}\n".format(me=me, bio=bio)
    if me:
        return "<b>About user:</b>\n{me}" "".format(me=me, bio=bio)
    return ""


__help__ = """
Writing something about yourself is cool, whether to make people know about yourself or \
promoting your profile.

All bios are displayed on /info command.

× /setbio <text>: While replying, will save another user's bio
× /bio: Will get your or another user's bio. This cannot be set by yourself.
× /setme <text>: Will set your info
× /me: Will get your or another user's info

An example of setting a bio for yourself:
`/setme I work for Telegram`; Bio is set to yourself.

An example of writing someone else' bio:
Reply to user's message: `/setbio He is such cool person`.

*Notice:* Do not use /setbio against yourself!
"""

__mod_name__ = "Bios/Abouts"

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio, run_async=True)
GET_BIO_HANDLER = DisableAbleCommandHandler(
    "bio", about_bio, pass_args=True, run_async=True
)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me, run_async=True)
GET_ABOUT_HANDLER = DisableAbleCommandHandler(
    "me", about_me, pass_args=True, run_async=True
)

dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)
