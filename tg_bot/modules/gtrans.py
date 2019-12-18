from typing import Optional, List

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher, LOGGER
from tg_bot.modules.disable import DisableAbleCommandHandler

from googletrans import Translator

#Translator based on google translate API

@run_async
def gtrans(bot: Bot, update: Update, args: List[str]):
    oky = " ".join(args)
    to_translate_text = update.effective_message.reply_to_message.text
    translator = Translator()
    try:
        translated = translator.translate(to_translate_text, dest=oky)
        oof = translated.src
        results = translated.text
        update.effective_message.reply_text("Translated from {} to {}.\n {}".format(oof, oky, results))
    except exc:
        update.effective_message.reply_text(str(exc))


__help__ = """- /tr - To translate to your language!
"""
__mod_name__ = "G Translate"

dispatcher.add_handler(DisableAbleCommandHandler("tr", gtrans, pass_args=True))

