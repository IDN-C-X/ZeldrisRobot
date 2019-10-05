import html
import json
from datetime import datetime
from typing import Optional, List
import requests
import subprocess
import os
import speedtest
import time
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.filters import CustomFilters

#Kanged from PaperPlane Extended userbot
def speed_convert(size):
    """
    Hi human, you can't read bytes?
    """
    power = 2**10
    zero = 0
    units = {0: '', 1: 'Kb/s', 2: 'Mb/s', 3: 'Gb/s', 4: 'Tb/s'}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"

@run_async
def get_bot_ip(bot: Bot, update: Update):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)

@run_async
def rtt(bot: Bot, update: Update):
    out = ""
    under = False
    if os.name == 'nt':
        output = subprocess.check_output("ping -n 1 1.0.0.1 | findstr time*", shell=True).decode()
        outS = output.splitlines()
        out = outS[0]
    else:
        out = subprocess.check_output("ping -c 1 1.0.0.1 | grep time=", shell=True).decode()
    splitOut = out.split(' ')
    stringtocut = ""
    for line in splitOut:
        if(line.startswith('time=') or line.startswith('time<')):
            stringtocut=line
            break
    newstra=stringtocut.split('=')
    if len(newstra) == 1:
        under = True
        newstra=stringtocut.split('<')
    newstr=""
    if os.name == 'nt':
        newstr=newstra[1].split('ms')
    else:
        newstr=newstra[1].split(' ') #redundant split, but to try and not break windows ping
    ping_time = float(newstr[0])
    if os.name == 'nt' and under:
        update.effective_message.reply_text(" Round-trip time is <{}ms".format(ping_time))
    else:
        update.effective_message.reply_text(" Round-trip time: {}ms".format(ping_time))

def ping(bot: Bot, update: Update):
    start_time = time.time()
    requests.get('https://api.telegram.org')
    end_time = time.time()
    ping_time = round(float(end_time - start_time)*1000, 2)
    
    update.effective_message.reply_text(" Telegram ping: {}ms".format(ping_time))

@run_async
def speedtst(bot: Bot, update: Update):
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    update.effective_message.reply_text("Download "
                   f"{speed_convert(result['download'])} \n"
                   "Upload "
                   f"{speed_convert(result['upload'])} \n"
                   "Ping "
                   f"{result['ping']} \n"
                   "ISP "
                   f"{result['client']['isp']}")

IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))
RTT_HANDLER = DisableAbleCommandHandler("ping", rtt, filters=CustomFilters.sudo_filter)
PING_HANDLER = DisableAbleCommandHandler("tgping", ping, filters=CustomFilters.sudo_filter)
SPEED_HANDLER = DisableAbleCommandHandler("speedtest", speedtst, filters=CustomFilters.sudo_filter) 

dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(RTT_HANDLER)
dispatcher.add_handler(SPEED_HANDLER)
dispatcher.add_handler(PING_HANDLER)
