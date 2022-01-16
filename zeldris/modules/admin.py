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
import os

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from zeldris import dispatcher
from zeldris.modules.connection import connected
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.admin_rights import (
    user_can_pin,
    user_can_promote,
    user_can_changeinfo,
)
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.chat_status import (
    bot_admin,
    can_promote,
    user_admin,
    ADMIN_CACHE,
    can_pin,
)
from zeldris.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from zeldris.modules.log_channel import loggable


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def promote(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat_id = update.effective_chat.id
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to promote someone!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("mention one.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status in ["administrator", "creator"]:
        message.reply_text("This person is already an admin...!")
        return ""

    if user_id == bot.id:
        message.reply_text("I hope, if i could promote myself!")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    bot.promoteChatMember(
        chat_id,
        user_id,
        can_change_info=bot_member.can_change_info,
        can_post_messages=bot_member.can_post_messages,
        can_edit_messages=bot_member.can_edit_messages,
        can_delete_messages=bot_member.can_delete_messages,
        can_invite_users=bot_member.can_invite_users,
        can_restrict_members=bot_member.can_restrict_members,
        can_pin_messages=bot_member.can_pin_messages,
    )

    title = "admin"
    if " " in message.text:
        title = message.text.split(" ", 1)[1]
        if len(title) > 16:
            message.reply_text(
                "The title length is longer than 16 characters.\nTruncating it to 16 characters."
            )

        try:
            bot.setChatAdministratorCustomTitle(chat.id, user_id, title)

        except BadRequest:
            message.reply_text(
                "I can't set custom title for admins that I didn't promote!"
            )

    message.reply_text(
        f"Promoted <b>{user_member.user.first_name or user_id}</b>"
        + f" with title <code>{title[:16]}</code>!",
        parse_mode=ParseMode.HTML,
    )
    # refresh admin cache
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass
    return (
        "<b>{}:</b>"
        "\n#PROMOTED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {}".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(user_member.user.id, user_member.user.first_name),
        )
    )


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def fullpromote(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to promote someone!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("mention one.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status in ["administrator", "creator"]:
        message.reply_text("This person is already an admin...!")
        return ""

    if user_id == bot.id:
        message.reply_text("I hope, if i could promote myself!")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    bot.promoteChatMember(
        chat.id,
        user_id,
        can_change_info=bot_member.can_change_info,
        can_post_messages=bot_member.can_post_messages,
        can_edit_messages=bot_member.can_edit_messages,
        can_delete_messages=bot_member.can_delete_messages,
        can_invite_users=bot_member.can_invite_users,
        can_promote_members=bot_member.can_promote_members,
        can_restrict_members=bot_member.can_restrict_members,
        can_pin_messages=bot_member.can_pin_messages,
        can_manage_voice_chats=bot_member.can_manage_voice_chats,
    )

    title = "admin"
    if " " in message.text:
        title = message.text.split(" ", 1)[1]
        if len(title) > 16:
            message.reply_text(
                "The title length is longer than 16 characters.\nTruncating it to 16 characters."
            )

        try:
            bot.setChatAdministratorCustomTitle(chat.id, user_id, title)

        except BadRequest:
            message.reply_text(
                "I can't set custom title for admins that I didn't promote!"
            )

    message.reply_text(
        f"Fully Promoted <b>{user_member.user.first_name or user_id}</b>"
        + f" with title <code>{title[:16]}</code>!",
        parse_mode=ParseMode.HTML,
    )
    return (
        "<b>{}:</b>"
        "\n#FULLPROMOTED"
        "\n<b>Admin:</b> {}"
        "\n<b>User:</b> {}".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(user_member.user.id, user_member.user.first_name),
        )
    )


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def demote(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("You don't have enough rights to demote someone!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("mention one.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status == "creator":
        message.reply_text("I'm not gonna demote Creator this group.... 🙄")
        return ""

    if user_member.status != "administrator":
        message.reply_text(
            "How I'm supposed to demote someone who is not even an admin!"
        )
        return ""

    if user_id == bot.id:
        message.reply_text("Yeahhh... Not gonna demote myself!")
        return ""

    try:
        bot.promoteChatMember(
            int(chat.id),
            int(user_id),
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_voice_chats=False,
        )
        message.reply_text(
            f"Successfully demoted <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )
        return (
            "<b>{}:</b>"
            "\n#DEMOTED"
            "\n<b>Admin:</b> {}"
            "\n<b>User:</b> {}".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(user_member.user.id, user_member.user.first_name),
            )
        )

    except BadRequest:
        message.reply_text(
            "Failed to demote. I might not be admin, or the admin status was appointed by another "
            "user, so I can't act upon them!"
        )
        return ""


@bot_admin
@can_pin
@user_admin
@loggable
@typing_action
def pin(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    is_group = chat.type not in ["private", "channel"]

    prev_message = update.effective_message.reply_to_message

    if user_can_pin(chat, user, bot.id) is False:
        message.reply_text("You are missing rights to pin a message!")
        return ""

    if not prev_message:
        message.reply_text("Reply to the message you want to pin!")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise
        return (
            "<b>{}:</b>"
            "\n#PINNED"
            "\n<b>Admin:</b> {}".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )

    return ""


@bot_admin
@can_pin
@user_admin
@loggable
@typing_action
def unpin(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_pin(chat, user, bot.id) is False:
        message.reply_text("You are missing rights to unpin a message!")
        return ""

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        elif excp.message == "Message to unpin not found":
            message.reply_text(
                "I can't see pinned message, Maybe already unpinned, or pin message to old!"
            )
        else:
            raise

    return (
        "<b>{}:</b>"
        "\n#UNPINNED"
        "\n<b>Admin:</b> {}".format(
            html.escape(chat.title), mention_html(user.id, user.first_name)
        )
    )


@user_admin
@typing_action
def refresh_admin(update: Update, _: CallbackContext):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("Admins cache refreshed!")


@bot_admin
@user_admin
@typing_action
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.effective_user
    msg = update.effective_message
    chat = update.effective_chat

    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
    else:
        if msg.chat.type == "private":
            msg.reply_text("This command is meant to use in chat not in PM")
            return ""
        chat = update.effective_chat

    if chat.username:
        msg.reply_text(chat.username)
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = context.bot.exportChatInviteLink(chat.id)
            msg.reply_text(invitelink, disable_web_page_preview=True)
        else:
            msg.reply_text(
                "I don't have access to the invite link, try changing my permissions!"
            )
    else:
        msg.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!"
        )


@typing_action
def adminlist(update: Update, _: CallbackContext):
    administrators = update.effective_chat.get_administrators()
    text = "Admins in <b>{}</b>:".format(update.effective_chat.title or "this chat")
    for admin in administrators:
        user = admin.user
        status = admin.status
        name = f"{(mention_html(user.id, user.first_name))}"
        if status == "creator":
            text += "\n 🦁 Creator:"
            text += "\n • {} \n\n 🦊 Admin:".format(name)
    for admin in administrators:
        user = admin.user
        status = admin.status
        name = f"{(mention_html(user.id, user.first_name))}"
        if status == "administrator":
            text += "\n • {}".format(name)
    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@bot_admin
@can_promote
@user_admin
@typing_action
def set_title(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except BadRequest:
        return

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    if user_member.status == "creator":
        message.reply_text(
            "This person CREATED the chat, how can i set custom title for him?"
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me."
        )
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
        message.reply_text(
            "Sucessfully set title for <b>{}</b> to <code>{}</code>!".format(
                user_member.user.first_name or user_id, title[:16]
            ),
            parse_mode=ParseMode.HTML,
        )

    except BadRequest:
        message.reply_text("I can't set custom title for admins that I didn't promote!")


@bot_admin
@user_admin
@typing_action
def setchatpic(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, bot.id) is False:
        msg.reply_text("You are missing right to change group info!")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("You can only set some photo as chat pic!")
            return
        dlmsg = msg.reply_text("Just a sec...")
        tpic = bot.getFile(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                bot.setChatPhoto(int(chat.id), photo=chatp)
                msg.reply_text("Successfully set new chatpic!")
        except BadRequest as excp:
            msg.reply_text(f"Error! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("Reply to some photo or file to set new chat pic!")


@bot_admin
@user_admin
@typing_action
def rmchatpic(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, bot.id) is False:
        msg.reply_text("You don't have enough rights to delete group photo")
        return
    try:
        bot.deleteChatPhoto(int(chat.id))
        msg.reply_text("Successfully deleted chat's profile photo!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@bot_admin
@user_admin
@typing_action
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args

    if user_can_changeinfo(chat, user, bot.id) is False:
        msg.reply_text("You don't have enough rights to change chat info!")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("Enter some text to set new title in your chat!")
        return

    try:
        bot.setChatTitle(int(chat.id), str(title))
        msg.reply_text(
            f"Successfully set <b>{title}</b> as new chat title!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")
        return


@bot_admin
@user_admin
@typing_action
def set_sticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, bot.id) is False:
        return msg.reply_text("You're missing rights to change chat info!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "You need to reply to some sticker to set chat sticker set!"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            bot.setChatStickerSet(chat.id, stkr)
            msg.reply_text(f"Successfully set new group stickers in {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "Sorry, due to telegram restrictions chat needs to have minimum 100 members before they can have "
                    "group stickers! "
                )
            msg.reply_text(f"Error! {excp.message}.")
    else:
        msg.reply_text("You need to reply to some sticker to set chat sticker set!")


@bot_admin
@user_admin
@typing_action
def set_desc(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, bot.id) is False:
        return msg.reply_text("You're missing rights to change chat info!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("Setting empty description won't do anything!")
    try:
        if len(desc) > 255:
            return msg.reply_text("Description must needs to be under 255 characters!")
        bot.setChatDescription(chat.id, desc)
        msg.reply_text(f"Successfully updated chat description in {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"Error! {excp.message}.")


def __chat_settings__(chat_id, user_id):
    return "You are *admin*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status
        in ("administrator", "creator")
    )


__help__ = """
Lazy to promote or demote someone for admins? Want to see basic information about chat? \
All stuff about chatroom such as admin lists, pinning or grabbing an invite link can be \
done easily using the bot.

× /adminlist: list of admins in the chat

*Admin only:*
× /pin: Silently pins the message replied to - add `loud`, `notify` or `violent` to give notificaton to users.
× /unpin: Unpins the currently pinned message.
× /invitelink: Gets private chat's invitelink.
× /promote `<title>`: Promotes the user replied to.
× /fullpromote `<title>`: Promotes the user replied to with ful rights.
× /demote: Demotes the user replied to.
× /settitle: Sets a custom title for an admin which is promoted by bot.
× /setgpic: As a reply to file or photo to set group profile pic!
× /delgpic: Same as above but to remove group profile pic.
× /setgtitle `<newtitle>`: Sets new chat title in your group.
× /setsticker: As a reply to some sticker to set it as group sticker set!
× /setdescription: <description> Sets new chat description in group.

*Note*: To set group sticker set chat must needs to have min 100 members.

An example of promoting someone to admins:
`/promote @username`; this promotes a user to admins.
"""

__mod_name__ = "Admins"

PIN_HANDLER = CommandHandler(
    "pin", pin, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
UNPIN_HANDLER = CommandHandler(
    "unpin", unpin, filters=Filters.chat_type.groups, run_async=True
)
ADMIN_REFRESH_HANDLER = CommandHandler("admincache", refresh_admin, run_async=True)
INVITE_HANDLER = CommandHandler("invitelink", invite, run_async=True)
CHAT_PIC_HANDLER = CommandHandler(
    "setgpic", setchatpic, filters=Filters.chat_type.groups, run_async=True
)
DEL_CHAT_PIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=Filters.chat_type.groups, run_async=True
)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=Filters.chat_type.groups, run_async=True
)
SETSTICKET_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=Filters.chat_type.groups, run_async=True
)
SETDESC_HANDLER = CommandHandler(
    "setdescription", set_desc, filters=Filters.chat_type.groups, run_async=True
)
PROMOTE_HANDLER = CommandHandler(
    "promote", promote, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
FULLPROMOTE_HANDLER = CommandHandler(
    "fullpromote",
    fullpromote,
    pass_args=True,
    filters=Filters.chat_type.groups,
    run_async=True,
)
DEMOTE_HANDLER = CommandHandler(
    "demote", demote, pass_args=True, filters=Filters.chat_type.groups, run_async=True
)
SET_TITLE_HANDLER = DisableAbleCommandHandler(
    "settitle", set_title, pass_args=True, run_async=True
)
ADMINLIST_HANDLER = DisableAbleCommandHandler(
    "adminlist", adminlist, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(CHAT_PIC_HANDLER)
dispatcher.add_handler(DEL_CHAT_PIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(SETSTICKET_HANDLER)
dispatcher.add_handler(SETDESC_HANDLER)
