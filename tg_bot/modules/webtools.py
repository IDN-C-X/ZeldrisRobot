import html
import json
from datetime import datetime
from typing import Optional, List
import requests
import os
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.filters import CustomFilters

@run_async
def get_bot_ip(bot: Bot, update: Update):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)

@run_async
def ping(bot: Bot, update: Update):
    start = datetime.now()
    hostname = "google.com" #example
    response = os.system("ping -c 1 " + hostname)
    end = datetime.now()
    ping_time = (end - start).microseconds / 1000
    update.effective_message.reply_text(" Ping speed was : {}ms".format(ping_time))

IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))
PING_HANDLER = DisableAbleCommandHandler("ping", ping, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(PING_HANDLER)
