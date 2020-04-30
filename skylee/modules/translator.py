from typing import Optional, List
from gtts import gTTS
import re
import os

from telegram import Message, Update, Bot, User, ChatAction, MessageEntity, ParseMode
from telegram.ext import Filters, MessageHandler, run_async

from skylee import dispatcher, LOGGER
from skylee.modules.disable import DisableAbleCommandHandler
from skylee.modules.helper_funcs.alternate import typing_action

from googletrans import Translator


@run_async
@typing_action
def gtrans(update, context):
    msg = update.effective_message
    args = context.args
    lang = " ".join(args)
    if not lang:
       lang = "en"
    to_translate_text = msg.reply_to_message.text
    translator = Translator()
    try:
        translated = translator.translate(to_translate_text, dest=lang)
        trl = translated.src
        results = translated.text
        msg.reply_text("Translated from {} to {}.\n {}".format(trl, lang, results))
    except :
        msg.reply_text("Error! text might have emojis or invalid language code.")


@run_async
def gtts(update, context):
    args = context.args
    try:
        reply = " ".join(args)
        if not reply:
            reply = update.effective_message.reply_to_message.text
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        tts = gTTS(reply)
        tts.save("skylee.mp3")
        with open("skylee.mp3", "rb") as x:
            linelist = list(x)
            linecount = len(linelist)
        if linecount == 1:
            update.message.chat.send_action(ChatAction.RECORD_AUDIO)
            tts = gTTS(reply)
            tts.save("skylee.mp3")
        with open("skylee.mp3", "rb") as speech:
            update.message.reply_voice(speech, quote=False)
            os.remove("skylee.mp3")
    except :
            update.effective_message.reply_text("Reply to some message or enter some text to convert it into audio format!")


__help__ = """
× /tr - To translate to your language, by default language is set to english, use `/tr <lang code>` for some other language!

× /tts - To some message to convert it into audio format! 
"""
__mod_name__ = "Translate"

dispatcher.add_handler(DisableAbleCommandHandler(["tr", "tl"], gtrans, pass_args=True))
dispatcher.add_handler(DisableAbleCommandHandler("tts", gtts, pass_args=True))
