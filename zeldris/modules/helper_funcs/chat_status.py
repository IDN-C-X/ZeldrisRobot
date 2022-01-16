#  ZeldrisRobot
#  Copyright (C) 2017-2019, Paul Larsen
#  Copyright (C) 2022 IDNCoderX Team, <https://github.com/IDN-C-X/ZeldrisRobot>
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


from functools import wraps
from threading import RLock

from cachetools import TTLCache
from telegram import Chat, ChatMember, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext

from zeldris import (
    DEL_CMDS,
    DEV_USERS,
    WHITELIST_USERS,
    dispatcher,
)

# refresh cache 10m
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10)
THREAD_LOCK = RLock()


def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


def is_user_ban_protected(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DEV_USERS
        or user_id in WHITELIST_USERS
        or chat.all_members_are_administrators
        or user_id in {777000, 1087968824}
    ):
        return True

    if not member:
        member = chat.get_member(user_id)
    return member.status in ("administrator", "creator")


def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DEV_USERS
        or user_id in {777000, 1087968824}
        or chat.all_members_are_administrators
    ):
        return True

    if not member:
        with THREAD_LOCK:
            # try to fetch from cache first.
            try:
                return user_id in ADMIN_CACHE[chat.id]
            except KeyError:
                # keyerror happend means cache is deleted,
                # so query bot api again and return user status
                # while saving it in cache for future useage...
                try:
                    chat_admins = dispatcher.bot.getChatAdministrators(chat.id)
                    admin_list = [x.user.id for x in chat_admins]
                    ADMIN_CACHE[chat.id] = admin_list

                    if user_id in admin_list:
                        return True
                except Unauthorized:
                    return False


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)
    return bot_member.status in ("administrator", "creator")


def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ("left", "kicked")


def bot_can_delete(func):
    @wraps(func)
    def delete_rights(update, context, *args, **kwargs):
        if can_delete(update.effective_chat, context.bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            "I can't delete messages here! "
            "Make sure I'm admin and can delete other user's messages."
        )

    return delete_rights


def can_pin(func):
    @wraps(func)
    def pin_rights(update, context, *args, **kwargs):
        if update.effective_chat.get_member(context.bot.id).can_pin_messages:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            "I can't pin messages here! " "Make sure I'm admin and can pin messages."
        )

    return pin_rights


def can_promote(func):
    @wraps(func)
    def promote_rights(update, context, *args, **kwargs):
        if update.effective_chat.get_member(context.bot.id).can_promote_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            "I can't promote/demote people here! "
            "Make sure I'm admin and can appoint new admins."
        )

    return promote_rights


def can_restrict(func):
    @wraps(func)
    def promote_rights(update, context, *args, **kwargs):
        if update.effective_chat.get_member(context.bot.id).can_restrict_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            "I can't restrict people here! "
            "Make sure I'm admin and can appoint new admins."
        )

    return promote_rights


def bot_admin(func):
    @wraps(func)
    def is_admin(update, context, *args, **kwargs):
        if is_bot_admin(update.effective_chat, context.bot.id):
            return func(update, context, *args, **kwargs)
        try:
            update.effective_message.reply_text("I'm not admin!")
        except BadRequest:
            return

    return is_admin


def user_admin(func):
    @wraps(func)
    def is_admin(update, context, *args, **kwargs):
        user = update.effective_user
        if user and is_user_admin(update.effective_chat, user.id):
            return func(update, context, *args, **kwargs)

        if not user:
            pass

        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except BadRequest:
                pass

        else:
            update.effective_message.reply_text(
                "You're missing admin rights for using this command!"
            )

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    def is_admin(update, context, *args, **kwargs):
        user = update.effective_user
        if user and is_user_admin(update.effective_chat, user.id):
            return func(update, context, *args, **kwargs)

        if not user:
            pass

        elif DEL_CMDS and " " not in update.effective_message.text:
            update.effective_message.delete()

    return is_admin


def user_not_admin(func):
    @wraps(func)
    def is_not_admin(update, context, *args, **kwargs):
        user = update.effective_user
        if user and not is_user_admin(update.effective_chat, user.id):
            return func(update, context, *args, **kwargs)

    return is_not_admin


def dev_plus(func):
    @wraps(func)
    def is_dev_plus_func(update, context, *args, **kwargs):
        user = update.effective_user

        if user.id in DEV_USERS:
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except BaseException:
                pass
        else:
            update.effective_message.reply_text(
                "This is a developer restricted command."
                " You do not have permissions to run this."
            )

    return is_dev_plus_func


def connection_status(func):
    @wraps(func)
    def connected_status(update: Update, context: CallbackContext, *args, **kwargs):
        conn = connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = dispatcher.bot.getChat(conn)
            update.__setattr__("_effective_chat", chat)
            return func(update, context, *args, **kwargs)
        if update.effective_message.chat.type == "private":
            update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first.",
            )
            return connected_status

        return func(update, context, *args, **kwargs)

    return connected_status


# Workaround for circular import with connection.py
from zeldris.modules import connection

connected = connection.connected
