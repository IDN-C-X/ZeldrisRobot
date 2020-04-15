import speedtest
import requests

from psutil import cpu_percent, virtual_memory
from platform import python_version
from telegram import __version__
from spamwatch import __version__ as __sw__
from pythonping import ping as ping3
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from skylee import dispatcher, OWNER_ID
from skylee.modules.helper_funcs.filters import CustomFilters


@run_async
def ping(update, context):
    tg_api = ping3('api.telegram.org', count=4)
    google = ping3('google.com', count=4)
    text = "*Pong!*\n"
    text += "Average speed to Telegram bot API server - `{}` ms\n".format(tg_api.rtt_avg_ms)
    if google.rtt_avg:
        gspeed = google.rtt_avg
    else:
        gspeed = google.rtt_avg
    text += "Average speed to Google - `{}` ms".format(gspeed)
    update.effective_message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

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
def get_bot_ip(update, context):
    """ Sends the bot's IP address, so as to be able to ssh in if necessary.
        OWNER ONLY.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)



@run_async
def speedtst(update, context):
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

@run_async
def system_status(update, context):
    msg = update.effective_message
    mem = virtual_memory()
    cpu = str(cpu_percent())
    status = "*System is online & running!*\n\n"
    status += "*CPU usage:* "+cpu+" %\n"
    status += "*Memory used:* "+str(mem[2])+" %\n\n"
    status += "*Python version:* "+python_version()+"\n"
    status += "*Library version:* "+str(__version__)+"\n"
    status += "*Spamwatch API:* "+str(__sw__)+"\n"
    msg.reply_text(status, parse_mode=ParseMode.MARKDOWN)


IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))
PING_HANDLER = CommandHandler("ping", ping, filters=CustomFilters.sudo_filter)
SPEED_HANDLER = CommandHandler("speedtest", speedtst, filters=CustomFilters.sudo_filter) 
SYS_STATUS_HANDLER = CommandHandler("sysinfo", system_status, filters=CustomFilters.sudo_filter)

dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(SPEED_HANDLER)
dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(SYS_STATUS_HANDLER)
