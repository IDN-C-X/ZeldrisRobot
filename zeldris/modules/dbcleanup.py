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


from time import sleep

from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, Filters

import zeldris.modules.sql.global_bans_sql as gban_sql
import zeldris.modules.sql.users_sql as user_sql
from zeldris import dispatcher, DEV_USERS


def get_invalid_chats(bot: Bot, update: Update, remove: bool = False):
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting invalid chats."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except BaseException:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)
        try:
            bot.get_chat(cid, timeout=120)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
        except BaseException:
            pass

    try:
        progress_message.delete()
    except BaseException:
        pass

    if remove:
        for muted_chat in chat_list:
            sleep(0.1)
            user_sql.rem_chat(muted_chat)

    return kicked_chats


def get_invalid_gban(bot: Bot, remove: bool = False):
    banned = gban_sql.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["user_id"]
        sleep(0.1)
        try:
            bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
        except BaseException:
            pass

    if remove:
        for user_id in ungban_list:
            sleep(0.1)
            gban_sql.ungban_user(user_id)

    return ungbanned_users


def dbcleanup(update: Update, context: CallbackContext):
    msg = update.effective_message

    msg.reply_text("Getting invalid chat count ...")
    invalid_chat_count = get_invalid_chats(context.bot, update)

    msg.reply_text("Getting invalid gbanned count ...")
    invalid_gban_count = get_invalid_gban(context.bot)

    reply = f"Total invalid chats - {invalid_chat_count}\n"
    reply += f"Total invalid gbanned users - {invalid_gban_count}"

    buttons = [[InlineKeyboardButton("Cleanup DB", callback_data="db_cleanup")]]

    update.effective_message.reply_text(
        reply, reply_markup=InlineKeyboardMarkup(buttons)
    )


def get_muted_chats(bot: Bot, update: Update, leave: bool = False):
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    muted_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting muted chats."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except BaseException:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)

        try:
            bot.send_chat_action(cid, "TYPING", timeout=120)
        except (BadRequest, Unauthorized):
            muted_chats += +1
            chat_list.append(cid)
        except BaseException:
            pass

    try:
        progress_message.delete()
    except BaseException:
        pass

    if leave:
        for muted_chat in chat_list:
            sleep(0.1)
            try:
                bot.leaveChat(muted_chat, timeout=120)
            except BaseException:
                pass
            user_sql.rem_chat(muted_chat)

    return muted_chats


def leave_muted_chats(update: Update, context: CallbackContext):
    message = update.effective_message
    progress_message = message.reply_text("Getting chat count ...")
    muted_chats = get_muted_chats(context.bot, update)

    buttons = [[InlineKeyboardButton("Leave chats", callback_data="db_leave_chat")]]

    update.effective_message.reply_text(
        f"I am muted in {muted_chats} chats.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    progress_message.delete()


def callback_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [DEV_USERS]

    bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat" and query.from_user.id in admin_list:
        bot.editMessageText("Leaving chats ...", chat_id, message.message_id)
        chat_count = get_muted_chats(bot, update, True)
        bot.sendMessage(chat_id, f"Left {chat_count} chats.")
    elif (
        query_type == "db_leave_chat"
        or query_type == "db_cleanup"
        and query.from_user.id not in admin_list
    ):
        query.answer("You are not allowed to use this.")
    elif query_type == "db_cleanup":
        bot.editMessageText("Cleaning up DB ...", chat_id, message.message_id)
        invalid_chat_count = get_invalid_chats(bot, update, True)
        invalid_gban_count = get_invalid_gban(bot, True)
        reply = "Cleaned up {} chats and {} gbanned users from db.".format(
            invalid_chat_count, invalid_gban_count
        )
        bot.sendMessage(chat_id, reply)


DB_CLEANUP_HANDLER = CommandHandler(
    "dbcleanup",
    dbcleanup,
    filters=Filters.user(DEV_USERS),
    run_async=True,
)
LEAVE_MUTED_CHATS_HANDLER = CommandHandler(
    "leavemutedchats",
    leave_muted_chats,
    filters=Filters.user(DEV_USERS),
    run_async=True,
)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", run_async=True)

dispatcher.add_handler(DB_CLEANUP_HANDLER)
dispatcher.add_handler(LEAVE_MUTED_CHATS_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)

__mod_name__ = "DB Cleanup"
__handlers__ = [DB_CLEANUP_HANDLER, LEAVE_MUTED_CHATS_HANDLER, BUTTON_HANDLER]
