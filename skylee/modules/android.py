import re, html, time
from bs4 import BeautifulSoup
from requests import get
from telegram import Message, Update, Bot, User, Chat, ParseMode, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import run_async
from telegram.utils.helpers import escape_markdown, mention_html

from skylee import dispatcher, updater
from skylee.modules.disable import DisableAbleCommandHandler
from skylee.modules.helper_funcs.alternate import typing_action

GITHUB = 'https://github.com'
DEVICES_DATA = 'https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json'

@run_async
@typing_action
def magisk(update, context):
    url = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/'
    releases = ""
    for type, branch in {"Stable":["master/stable","master"], "Beta":["master/beta","master"], "Canary (release)":["canary/release","canary"], "Canary (debug)":["canary/debug","canary"]}.items():
        data = get(url + branch[0] + '.json').json()
        releases += f'*{type}*: \n' \
                    f'• [Changelog](https://github.com/topjohnwu/magisk_files/blob/{branch[1]}/notes.md)\n' \
                    f'• Zip - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) \n' \
                    f'• App - [{data["app"]["version"]}-{data["app"]["versionCode"]}]({data["app"]["link"]}) \n' \
                    f'• Uninstaller - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["uninstaller"]["link"]})\n\n'


    del_msg = update.message.reply_text("*Latest Magisk Releases:*\n{}".format(releases),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    time.sleep(300)
    try:
        del_msg.delete()
        update.effective_message.delete()
    except BadRequest as err:
        if (err.message == "Message to delete not found" ) or (err.message == "Message can't be deleted" ):
            return

@run_async
@typing_action
def device(update, context):
    args = context.args
    if len(args) == 0:
        reply = f'No codename provided, write a codename for fetching informations.'
        del_msg = update.effective_message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found" ) or (err.message == "Message can't be deleted" ):
                return
    device = " ".join(args)
    db = get(DEVICES_DATA).json()
    newdevice = device.strip('lte') if device.startswith('beyond') else device
    try:
        reply = f'Search results for {device}:\n\n'
        brand = db[newdevice][0]['brand']
        name = db[newdevice][0]['name']
        model = db[newdevice][0]['model']
        codename = newdevice
        reply += f'<b>{brand} {name}</b>\n' \
            f'Model: <code>{model}</code>\n' \
            f'Codename: <code>{codename}</code>\n\n'
    except KeyError as err:
        reply = f"Couldn't find info about {device}!\n"
        del_msg = update.effective_message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found" ) or (err.message == "Message can't be deleted" ):
                return
    update.message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@run_async
@typing_action
def twrp(update, context):
    args = context.args
    if len(args) == 0:
        reply='No codename provided, write a codename for fetching informations.'
        del_msg = update.effective_message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found" ) or (err.message == "Message can't be deleted" ):
                return

    device = " ".join(args)
    url = get(f'https://eu.dl.twrp.me/{device}/')
    if url.status_code == 404:
        reply = f"Couldn't find twrp downloads for {device}!\n"
        del_msg = update.effective_message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if (err.message == "Message to delete not found" ) or (err.message == "Message can't be deleted" ):
                return
    else:
        reply = f'*Latest Official TWRP for {device}*\n'
        db = get(DEVICES_DATA).json()
        newdevice = device.strip('lte') if device.startswith('beyond') else device
        try:
            brand = db[newdevice][0]['brand']
            name = db[newdevice][0]['name']
            reply += f'*{brand} - {name}*\n'
        except KeyError as err:
            pass
        page = BeautifulSoup(url.content, 'lxml')
        date = page.find("em").text.strip()
        reply += f'*Updated:* {date}\n'
        trs = page.find('table').find_all('tr')
        row = 2 if trs[0].find('a').text.endswith('tar') else 1
        for i in range(row):
            download = trs[i].find('a')
            dl_link = f"https://eu.dl.twrp.me{download['href']}"
            dl_file = download.text
            size = trs[i].find("span", {"class": "filesize"}).text
            reply += f'[{dl_file}]({dl_link}) - {size}\n'

        update.message.reply_text("{}".format(reply),
                               parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

__help__ = """
Get Latest magisk relese, Twrp for your device or info about some device using its codename, Directly from Bot!

*Android related commands:*

 × /magisk - Gets the latest magisk release for Stable/Beta/Canary.
 × /device <codename> - Gets android device basic info from its codename.
 × /twrp <codename> -  Gets latest twrp for the android device using the codename.
"""

__mod_name__ = "Android"

MAGISK_HANDLER = DisableAbleCommandHandler("magisk", magisk)
DEVICE_HANDLER = DisableAbleCommandHandler("device", device, pass_args=True)
TWRP_HANDLER = DisableAbleCommandHandler("twrp", twrp, pass_args=True)

dispatcher.add_handler(MAGISK_HANDLER)
dispatcher.add_handler(DEVICE_HANDLER)
dispatcher.add_handler(TWRP_HANDLER)
