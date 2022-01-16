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


from typing import Optional

from telegram import Message, User, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

import zeldris.modules.sql.rules_sql as sql
from zeldris import dispatcher
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.chat_status import user_admin
from zeldris.modules.helper_funcs.string_handling import markdown_parser


@typing_action
def get_rules(update: Update, _: CallbackContext):
    chat_id = update.effective_chat.id
    send_rules(update, chat_id)


# Do not async - not from a handler
def send_rules(update, chat_id, from_pm=False):
    bot = dispatcher.bot
    user = update.effective_user  # type: Optional[User]
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message != "Chat not found" or not from_pm:
            raise

        bot.send_message(
            user.id,
            "The rules shortcut for this chat hasn't been set properly! Ask admins to "
            "fix this.",
        )
        return
    rules = sql.get_rules(chat_id)
    text = "The rules for *{}* are:\n\n{}".format(escape_markdown(chat.title), rules)

    if from_pm and rules:
        bot.send_message(user.id, text, parse_mode=ParseMode.MARKDOWN)
    elif from_pm:
        bot.send_message(
            user.id,
            "The group admins haven't set any rules for this chat yet. "
            "This probably doesn't mean it's lawless though...!",
        )
    elif rules:
        update.effective_message.reply_text(
            "Contact me in PM to get this group's rules.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Rules",
                            url="t.me/{}?start={}".format(bot.username, chat_id),
                        )
                    ]
                ]
            ),
        )
    else:
        update.effective_message.reply_text(
            "The group admins haven't set any rules for this chat yet. "
            "This probably doesn't mean it's lawless though...!"
        )


@user_admin
@typing_action
def set_rules(update: Update, _: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    raw_text = msg.text
    args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(
            txt, entities=msg.parse_entities(), offset=offset
        )

        sql.set_rules(chat_id, markdown_rules)
        update.effective_message.reply_text("Successfully set rules for this group.")


@user_admin
@typing_action
def clear_rules(update: Update, _: CallbackContext):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    update.effective_message.reply_text("Successfully cleared rules!")


def __stats__():
    return "× {} chats have rules set.".format(sql.num_chats())


def __import_data__(chat_id, data):
    # set chat rules
    rules = data.get("info", {}).get("rules", "")
    sql.set_rules(chat_id, rules)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return "This chat has had it's rules set: `{}`".format(bool(sql.get_rules(chat_id)))


__help__ = """
Every chat works with different rules; this module will help make those rules clearer!

× /rules: get the rules for this chat.

*Admin only:*
× /setrules `<your rules here>`: Sets rules for the chat.
× /clearrules: Clears saved rules for the chat.
"""

__mod_name__ = "Rules"

GET_RULES_HANDLER = CommandHandler(
    "rules", get_rules, filters=Filters.chat_type.groups, run_async=True
)
SET_RULES_HANDLER = CommandHandler(
    "setrules", set_rules, filters=Filters.chat_type.groups, run_async=True
)
RESET_RULES_HANDLER = CommandHandler(
    "clearrules", clear_rules, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
