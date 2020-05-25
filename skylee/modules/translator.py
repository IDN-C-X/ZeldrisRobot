from typing import Optional, List
from gtts import gTTS
import re
import os
import requests
import json
from emoji import UNICODE_EMOJI

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
    translate_text = msg.reply_to_message.text
    ignore_text = UNICODE_EMOJI.keys()
    for emoji in ignore_text:
        if emoji in translate_text:
           translate_text = translate_text.replace(emoji, '')

    translator = Translator()
    try:
        translated = translator.translate(translate_text, dest=lang)
        trl = translated.src
        results = translated.text
        msg.reply_text("Translated from {} to {}.\n {}".format(trl, lang, results))
    except :
        msg.reply_text("Error! invalid language code.")


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


# Open API key
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"

@run_async
@typing_action
def spellcheck(update, context):
    if update.effective_message.reply_to_message:
        msg = update.effective_message.reply_to_message

        params = dict(lang="US", clientVersion="2.0",
                 apiKey=API_KEY, text=msg.text)

        res = requests.get(URL, params=params)
        changes = json.loads(res.text).get('LightGingerTheTextResult')
        curr_string = ""
        prev_end = 0

        for change in changes:
            start = change.get('From')
            end = change.get('To') + 1
            suggestions = change.get('Suggestions')
            if suggestions:
                sugg_str = suggestions[0].get('Text')  # should look at this list more
                curr_string += msg.text[prev_end:start] + sugg_str
                prev_end = end

        curr_string += msg.text[prev_end:]
        update.effective_message.reply_text(curr_string)
    else:
       update.effective_message.reply_text(
              "Reply to some message to get grammar corrected text!")


__help__ = """
× /tr or /tl: - To translate to your language, by default language is set to english, use `/tr <lang code>` for some other language!
× /splcheck: - As a reply to get grammar corrected text of gibberish message.
× /tts: - To some message to convert it into audio format!
"""
__mod_name__ = "Translate"

dispatcher.add_handler(DisableAbleCommandHandler(["tr", "tl"], gtrans, pass_args=True))
dispatcher.add_handler(DisableAbleCommandHandler("tts", gtts, pass_args=True))
dispatcher.add_handler(DisableAbleCommandHandler("splcheck", spellcheck))
