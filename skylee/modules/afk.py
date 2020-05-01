from typing import Optional
import random

from telegram import Message, Update, Bot, User
from telegram import MessageEntity, ParseMode
from telegram.error import BadRequest
from telegram.ext import Filters, MessageHandler, run_async

from skylee import dispatcher
from skylee.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
from skylee.modules.sql import afk_sql as sql
from skylee.modules.users import get_user_id

from skylee.modules.helper_funcs.alternate import send_message
import skylee.modules.helper_funcs.fun_strings as fun

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(update, context):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2:
        reason = args[1]
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    afkstr = random.choice(fun.AFK)
    update.effective_message.reply_text(afkstr.format(update.effective_user.first_name))


@run_async
def no_longer_afk(update, context):
    user = update.effective_user  # type: Optional[User]

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
       noafkstr = random.choice(fun.NOAFK)
       update.effective_message.reply_text(noafkstr.format(user.first_name))


@run_async
def reply_afk(update, context):
    message = update.effective_message  # type: Optional[Message]

    entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
    if message.entities and entities:
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(message.text[ent.offset:ent.offset + ent.length])
                if not user_id:
                    # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                    return
                try:
                    chat = context.bot.get_chat(user_id)
                except BadRequest:
                    print("Error in afk can't get user id {}".format(user_id))
                    return
                fst_name = chat.first_name

            else:
                return

            if sql.is_afk(user_id):
                valid, reason = sql.check_afk_status(user_id)
                if valid:
                    if not reason:
                        rplafkstr = random.choice(fun.AFKRPL)
                        res = rplafkstr.format(fst_name)
                    else:
                        res = f"<b>{fst_name}</b> is away from keyboard! says it's because of \n{reason}"
                    send_message(update.effective_message, res, parse_mode=ParseMode.HTML)


def __user_info__(user_id):
    is_afk = sql.is_afk(user_id)

    text = "<b>Currently AFK</b>: {}"
    if is_afk:
        text = text.format("Yes")

    else:
        text = text.format("No")
    return text

def __gdpr__(user_id):
    sql.rm_afk(user_id)



AFK_HANDLER = DisableAbleCommandHandler("afk", afk)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(Filters.regex("(?i)brb"), afk, friendly="afk")
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.group & ~Filters.update.edited_message, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.all & Filters.group , reply_afk)
# AFK_REPLY_HANDLER = MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION),
#                                   reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)
