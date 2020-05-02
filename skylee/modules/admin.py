import html
import os
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown, mention_html

from skylee import dispatcher
from skylee.modules.disable import DisableAbleCommandHandler
from skylee.modules.helper_funcs.chat_status import bot_admin, can_promote, user_admin, can_pin
from skylee.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from skylee.modules.helper_funcs.admin_rights import user_can_pin, user_can_promote
from skylee.modules.helper_funcs.alternate import typing_action
from skylee.modules.connection import connected
from skylee.modules.log_channel import loggable


@run_async
@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def promote(update, context):
    chat_id = update.effective_chat.id
    message = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    args = context.args

    if user_can_promote(chat, user, context.bot.id) == False:
    	message.reply_text("You don't have enough rights to promote someone!")
    	return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("mention one.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status == 'administrator' or user_member.status == 'creator':
        message.reply_text("Bruh! this guy is already an admin?")
        return ""

    if user_id == context.bot.id:
        message.reply_text("I wish, if i could promote myself!")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(context.bot.id)

    context.bot.promoteChatMember(chat_id, user_id,
                          can_change_info=bot_member.can_change_info,
                          can_post_messages=bot_member.can_post_messages,
                          can_edit_messages=bot_member.can_edit_messages,
                          can_delete_messages=bot_member.can_delete_messages,
                          can_invite_users=bot_member.can_invite_users,
                          can_restrict_members=bot_member.can_restrict_members,
                          can_pin_messages=bot_member.can_pin_messages)

    message.reply_text("promoted🧡")
    return "<b>{}:</b>" \
           "\n#PROMOTED" \
           "\n<b>Admin:</b> {}" \
           "\n<b>User:</b> {}".format(html.escape(chat.title),
                                      mention_html(user.id, user.first_name),
                                      mention_html(user_member.user.id, user_member.user.first_name))


@run_async
@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def demote(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user  # type: Optional[User]
    args = context.args

    if user_can_promote(chat, user, context.bot.id) == False:
    	message.reply_text("You don't have enough rights to demote someone!")
    	return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("mention one.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status == 'creator':
        message.reply_text("I'm not gonna demote Creator this group.... 🙄")
        return ""

    if not user_member.status == 'administrator':
        message.reply_text("How I'm supposed to demote someone who wasn't promoted!")
        return ""

    if user_id == context.bot.id:
        message.reply_text("Yeahhh... Not gonna demote myself!")
        return ""

    try:
        context.bot.promoteChatMember(int(chat.id), int(user_id),
                              can_change_info=False,
                              can_post_messages=False,
                              can_edit_messages=False,
                              can_delete_messages=False,
                              can_invite_users=False,
                              can_restrict_members=False,
                              can_pin_messages=False)
        message.reply_text("Successfully demoted!")
        return "<b>{}:</b>" \
               "\n#DEMOTED" \
               "\n<b>Admin:</b> {}" \
               "\n<b>User:</b> {}".format(html.escape(chat.title),
                                          mention_html(user.id, user.first_name),
                                          mention_html(user_member.user.id, user_member.user.first_name))

    except BadRequest:
        message.reply_text("Failed to demote. I might not be admin, or the admin status was appointed by another "
                           "user, so I can't act upon them!")
        return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
@typing_action
def pin(update, context):
    args = context.args
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]

    is_group = chat.type != "private" and chat.type != "channel"

    prev_message = update.effective_message.reply_to_message

    if user_can_pin(chat, user, context.bot.id) == False:
    	message.reply_text("You don't have enough rights to pin a message!")
    	return ""

    is_silent = True
    if len(args) >= 1:
        is_silent = not (args[0].lower() == 'notify' or args[0].lower() == 'loud' or args[0].lower() == 'violent')

    if prev_message and is_group:
        try:
            context.bot.pinChatMessage(chat.id, prev_message.message_id, disable_notification=is_silent)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        return "<b>{}:</b>" \
               "\n#PINNED" \
               "\n<b>Admin:</b> {}".format(html.escape(chat.title), mention_html(user.id, user.first_name))

    return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
@typing_action
def unpin(update, context):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    if user_can_pin(chat, user, context.bot.id) == False:
    	message.reply_text("You don't have enough rights to unpin a message!")
    	return ""

    try:
        context.bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    return "<b>{}:</b>" \
           "\n#UNPINNED" \
           "\n<b>Admin:</b> {}".format(html.escape(chat.title),
                                       mention_html(user.id, user.first_name))


@run_async
@bot_admin
@user_admin
@typing_action
def invite(update, context):
        user = update.effective_user
        msg = update.effective_message
        chat = update.effective_chat
        args = context.args

        conn = connected(context.bot, update, chat, user.id, need_admin=True)
        if conn:
                chat = dispatcher.bot.getChat(conn)
                chat_id = conn
                chat_name = dispatcher.bot.getChat(conn).title
        else:
                if msg.chat.type == "private":
                        msg.reply_text("This command is meant to use in chat not in PM")
                        return ""
                chat = update.effective_chat
                chat_id = update.effective_chat.id
                chat_name = update.effective_message.chat.title

        if chat.username:
                msg.reply_text(chat.username)
        elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
                bot_member = chat.get_member(context.bot.id)
                if bot_member.can_invite_users:
                        invitelink = context.bot.exportChatInviteLink(chat.id)
                        msg.reply_text(invitelink)
                else:
                        msg.reply_text("I don't have access to the invite link, try changing my permissions!")
        else:
                msg.reply_text("I can only give you invite links for supergroups and channels, sorry!")


@run_async
@typing_action
def adminlist(update, context):
    administrators = update.effective_chat.get_administrators()
    text = "Admins in *{}*:".format(update.effective_chat.title or "this chat")
    for admin in administrators:
        user = admin.user
        status = admin.status
        name = "[{}](tg://user?id={})".format(user.first_name + " " + (user.last_name or ""), user.id)
        if user.username:
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
        if status == "creator":
            text += "\n 🔱 Creator:"
            text += "\n` • `{} \n\n 🔰 Admin:".format(name)
    for admin in administrators:
        user = admin.user
        status = admin.status
        name = "[{}](tg://user?id={})".format(user.first_name + " " + (user.last_name or ""), user.id)
        if user.username:
            name = "[{}](tg://user?id={})".format(user.first_name + (user.last_name or ""), user.id)
        if status == "administrator":
            text += "\n` • `{}".format(name)
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@run_async
@bot_admin
@can_promote
@user_admin
@typing_action
def set_title(update, context):
    args = context.args
    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    if user_member.status == 'creator':
        message.reply_text("This person CREATED the chat, how can i set custom title for him?")
        return

    if not user_member.status == 'administrator':
        message.reply_text("Can't set title for non-admins!\nPromote them first to set custom title!")
        return

    if user_id == context.bot.id:
        message.reply_text("I can't set my own title myself! Get the one who made me admin to do it for me.")
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text("The title length is longer than 16 characters.\nTruncating it to 16 characters.")

    try:
        context.bot.set_chat_administrator_custom_title(chat.id, user_id, title)
        message.reply_text("Sucessfully set title for <b>{}</b> to <code>{}</code>!".format(user_member.user.first_name or user_id, title[:16]), parse_mode=ParseMode.HTML)

    except BadRequest:
        message.reply_text("I can't set custom title for admins that I didn't promote!")


@run_async
@bot_admin
@user_admin
@typing_action
def setchatpic(update,context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    user_member = chat.get_member(user.id)
    if user_member.can_change_info == False:
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
       dlmsg = msg.reply_text("Hold on...")
       tpic = context.bot.get_file(pic_id)
       tpic.download('gpic.png')
       try:
          with open('gpic.png', 'rb') as chatp:
               context.bot.set_chat_photo(int(chat.id), photo=chatp)
               msg.reply_text("Successfully set new chatpic!")
       except BadRequest as excp:
          msg.reply_text(f"Error! {excp.message}")
       finally:
          dlmsg.delete()
          if os.path.isfile('gpic.png'):
             os.remove("gpic.png")
    else:
          msg.reply_text("Reply to some photo or file to set new chat pic!")


@run_async
@bot_admin
@user_admin
@typing_action
def rmchatpic(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    user_member = chat.get_member(user.id)
    if user_member.can_change_info == False:
       msg.reply_text("You don't have enough rights to delete group photo")
       return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("Successfully deleted chat's profile photo!")
    except BadRequest as excp:
       msg.reply_text(f"Error! {excp.message}.")
       return


@run_async
@bot_admin
@user_admin
@typing_action
def setchat_title(update, context):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    user_member = chat.get_member(user.id)
    if user_member.can_change_info == False:
       msg.reply_text("You don't have enough rights to change chat info!")
       return

    title = " ".join(args)
    if not title:
       msg.reply_text("Enter some text to set new title in your chat!")
       return

    try:
       context.bot.set_chat_title(int(chat.id), str(title))
       msg.reply_text(f"Successfully set <b>{title}</b> as new chat title!", parse_mode=ParseMode.HTML)
    except BadRequest as excp:
       msg.reply_text(f"Error! {excp.message}.")
       return


def __chat_settings__(chat_id, user_id):
    return "You are *admin*: `{}`".format(
        dispatcher.bot.get_chat_member(chat_id, user_id).status in ("administrator", "creator"))


__help__ = """
Lazy to promote or demote someone for admins? Want to see basic information about chat? \
All stuff about chatroom such as admin lists, pinning or grabbing an invite link can be \
done easily using the bot.

 × /adminlist: list of admins in the chat

*Admin only:*
 × /pin: Silently pins the message replied to - add `loud`, `notify` or `violent` to give notificaton to users.
 × /unpin: Unpins the currently pinned message.
 × /invitelink: Gets private chat's invitelink.
 × /promote: Promotes the user replied to.
 × /demote: Demotes the user replied to.
 × /settitle: Sets a custom title for an admin which is promoted by bot.
 × /setgpic: As a reply to file or photo to set group profile pic!
 × /delgpic: Same as above but to remove group profile pic.
 × /setgtitle <newtitle>: Sets new chat title in your group.

An example of promoting someone to admins:
`/promote @username`; this promotes a user to admins.
"""

__mod_name__ = "Admin"

PIN_HANDLER = CommandHandler("pin", pin, pass_args=True, filters=Filters.group)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.group)

INVITE_HANDLER = CommandHandler("invitelink", invite)
CHAT_PIC_HANDLER = CommandHandler("setgpic", setchatpic, filters=Filters.group)
DEL_CHAT_PIC_HANDLER = CommandHandler("delgpic", rmchatpic, filters=Filters.group)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title, filters=Filters.group)

PROMOTE_HANDLER = CommandHandler("promote", promote, pass_args=True, filters=Filters.group)
DEMOTE_HANDLER = CommandHandler("demote", demote, pass_args=True, filters=Filters.group)

SET_TITLE_HANDLER = DisableAbleCommandHandler("settitle", set_title, pass_args=True)
ADMINLIST_HANDLER = DisableAbleCommandHandler("adminlist", adminlist, filters=Filters.group)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(CHAT_PIC_HANDLER)
dispatcher.add_handler(DEL_CHAT_PIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
