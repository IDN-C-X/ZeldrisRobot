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


import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from hurry.filesize import size as sizee
from requests import get
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from ujson import loads

from zeldris import dispatcher
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action

GITHUB = "https://github.com"
DEVICES_DATA = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@typing_action
def magisk(update: Update, _: CallbackContext):
    url = "https://raw.githubusercontent.com/topjohnwu/magisk-files/"
    releases = ""
    for types, branch in {
        "Stable": ["master/stable", "master"],
        "Canary": ["master/canary", "canary"],
    }.items():
        data = get(url + branch[0] + ".json").json()
        if types != "Canary":
            releases += (
                f"*{types}*: \n"
                f'• App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - ['
                f'Changelog]({data["magisk"]["note"]})\n \n'
            )
        else:
            releases += (
                f"*{types}*: \n"
                f'• App - [{data["magisk"]["version"]}-{data["magisk"]["versionCode"]}]({data["magisk"]["link"]}) - ['
                f'Changelog]({data["magisk"]["note"]})\n'
                f"\n Now magisk is packed as all in one, "
                f"refer [this installation](https://topjohnwu.github.io/Magisk/install.html) procedure for more info.\n"
            )

    update.message.reply_text(
        "*Latest Magisk Releases:*\n\n{}".format(releases),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


@typing_action
def device(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    devices = " ".join(args)
    db = get(DEVICES_DATA).json()
    newdevice = devices.strip("lte") if devices.startswith("beyond") else devices
    try:
        reply = f"Search results for {devices}:\n\n"
        brand = db[newdevice][0]["brand"]
        name = db[newdevice][0]["name"]
        model = db[newdevice][0]["model"]
        codename = newdevice
        reply += (
            f"<b>{brand} {name}</b>\n"
            f"Model: <code>{model}</code>\n"
            f"Codename: <code>{codename}</code>\n\n"
        )
    except KeyError:
        reply = f"Couldn't find info about {devices}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    update.message.reply_text(
        "{}".format(reply), parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


@typing_action
def twrp(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        reply = "No codename provided, write a codename for fetching informations."
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return

    _device = " ".join(args)
    url = get(f"https://eu.dl.twrp.me/{_device}/")
    if url.status_code == 404:
        reply = f"Couldn't find twrp downloads for {_device}!\n"
        del_msg = update.effective_message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        time.sleep(5)
        try:
            del_msg.delete()
            update.effective_message.delete()
        except BadRequest as err:
            if err.message in [
                "Message to delete not found",
                "Message can't be deleted",
            ]:
                return
    else:
        reply = f"*Latest Official TWRP for {_device}*\n"
        db = get(DEVICES_DATA).json()
        newdevice = _device.strip("lte") if _device.startswith("beyond") else _device
        try:
            brand = db[newdevice][0]["brand"]
            name = db[newdevice][0]["name"]
            reply += f"*{brand} - {name}*\n"
        except KeyError:
            pass
        page = BeautifulSoup(url.content, "lxml")
        date = page.find("em").text.strip()
        reply += f"*Updated:* {date}\n"
        trs = page.find("table").find_all("tr")

        # find latest version
        base_ver = (0, 0, 0)
        idx = 0
        for i, tag in enumerate(trs):
            dl_path = tag.find("a")["href"]
            match = re.search(r"([\d.]+)", dl_path)
            new_ver = tuple(int(x) for x in match.group(1).split("."))
            if new_ver > base_ver:
                base_ver = new_ver
                idx = i

        download = trs[idx].find("a")
        dl_link = f"https://eu.dl.twrp.me{download['href']}"
        dl_file = download.text
        size = trs[idx].find("span", {"class": "filesize"}).text
        reply += f"[{dl_file}]({dl_link}) - {size}\n"

        update.message.reply_text(
            "{}".format(reply),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


# Picked from AstrakoBot; Thanks to them!
@typing_action
def orangefox(update: Update, _: CallbackContext):
    message = update.effective_message
    devices = message.text[len("/orangefox ") :]
    btn = ""

    if devices:
        link = get(
            f"https://api.orangefox.download/v3/releases/?codename={devices}&sort=date_desc&limit=1"
        )

        if link.status_code == 404:
            msg = f"OrangeFox recovery is not avaliable for {devices}"
        else:
            page = loads(link.content)
            file_id = page["data"][0]["_id"]
            link = get(
                f"https://api.orangefox.download/v3/devices/get?codename={devices}"
            )
            page = loads(link.content)
            oem = page["oem_name"]
            model = page["model_name"]
            full_name = page["full_name"]
            maintainer = page["maintainer"]["username"]
            link = get(f"https://api.orangefox.download/v3/releases/get?_id={file_id}")
            page = loads(link.content)
            dl_file = page["filename"]
            build_type = page["type"]
            version = page["version"]
            changelog = page["changelog"][0]
            size = str(round(float(page["size"]) / 1024 / 1024, 1)) + "MB"
            dl_link = page["mirrors"]["US"]
            date = datetime.fromtimestamp(page["date"])
            md5 = page["md5"]
            msg = f"*Latest OrangeFox Recovery for the {full_name}*\n\n"
            msg += f"• Manufacturer: `{oem}`\n"
            msg += f"• Model: `{model}`\n"
            msg += f"• Codename: `{devices}`\n"
            msg += f"• Build type: `{build_type}`\n"
            msg += f"• Maintainer: `{maintainer}`\n"
            msg += f"• Version: `{version}`\n"
            msg += f"• Changelog: `{changelog}`\n"
            msg += f"• Size: `{size}`\n"
            msg += f"• Date: `{date}`\n"
            msg += f"• File: `{dl_file}`\n"
            msg += f"• MD5: `{md5}`\n"
            btn = [[InlineKeyboardButton(text="Download", url=dl_link)]]
    else:
        msg = "Enter the device codename to fetch, like:\n`/orangefox lavender`"

    update.message.reply_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


# Picked from UserIndoBot; Thanks to them!
@typing_action
def los(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    args = context.args
    try:
        device_ = args[0]
    except IndexError:
        device_ = ""

    if not device_:
        reply_text = "*Please Type Your Device Codename*\nExample : `/los lavender`"
        message.reply_text(
            reply_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    fetch = get(f"https://download.lineageos.org/api/v1/{device_}/nightly/*")
    if fetch.status_code == 200 and len(fetch.json()["response"]) != 0:
        usr = fetch.json()
        data = len(usr["response"]) - 1  # the latest rom are below
        response = usr["response"][data]
        filename = response["filename"]
        url = response["url"]
        buildsize_a = response["size"]
        buildsize_b = sizee(int(buildsize_a))
        version = response["version"]

        reply_text = f"*Download :* [{filename}]({url})\n"
        reply_text += f"*Build Size :* `{buildsize_b}`\n"
        reply_text += f"*Version :* `{version}`\n"

        keyboard = [
            [InlineKeyboardButton(text="Click Here To Downloads", url=f"{url}")]
        ]
        message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    else:
        message.reply_text(
            "`Couldn't find any results matching your query.`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


@typing_action
def gsi(update: Update, _: CallbackContext):
    message = update.effective_message

    usr = get(
        "https://api.github.com/repos/phhusson/treble_experimentations/releases/latest"
    ).json()
    reply_text = "*Gsi'S Latest release*\n"
    for i in range(len(usr)):
        try:
            name = usr["assets"][i]["name"]
            url = usr["assets"][i]["browser_download_url"]
            reply_text += f"[{name}]({url})\n"
        except IndexError:
            continue
    message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)


@typing_action
def bootleg(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    args = context.args
    try:
        codename = args[0]
    except IndexError:
        codename = ""

    if not codename:
        message.reply_text(
            "*Please Type Your Device Codename*\nExample : `/bootleg lavender`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    fetch = get("https://bootleggersrom-devices.github.io/api/devices.json")
    if fetch.status_code == 200:
        data = fetch.json()

        if codename.lower() == "x00t":
            devicea = "X00T"
        elif codename.lower() == "rmx1971":
            devicea = "RMX1971"
        else:
            devicea = codename.lower()

        try:
            fullname = data[devicea]["fullname"]
            filename = data[devicea]["filename"]
            buildate = data[devicea]["buildate"]
            buildsize = data[devicea]["buildsize"]
            buildsize = sizee(int(buildsize))
            downloadlink = data[devicea]["download"]
            if data[devicea]["mirrorlink"] != "":
                mirrorlink = data[devicea]["mirrorlink"]
            else:
                mirrorlink = None
        except KeyError:
            message.reply_text(
                "`Couldn't find any results matching your query.`",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )
            return

        reply_text = f"*BootlegersROM for {fullname}*\n"
        reply_text += f"*Download :* [{filename}]({downloadlink})\n"
        reply_text += f"*Size :* `{buildsize}`\n"
        reply_text += f"*Build Date :* `{buildate}`\n"
        if mirrorlink is not None:
            reply_text += f"[Mirror link]({mirrorlink})"

        keyboard = [
            [
                InlineKeyboardButton(
                    text="Click Here To Downloads", url=f"{downloadlink}"
                )
            ]
        ]

        message.reply_text(
            reply_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return

    elif fetch.status_code == 404:
        message.reply_text(
            "`Couldn't reach api`",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return


__help__ = """
Get the latest Magsik releases or TWRP for your device!

*Android related commands:*
× /magisk: Gets the latest magisk release for Stable/Beta/Canary.
× /device `<codename>`: Gets android device basic info from its codename.
× /twrp `<codename>`:  Gets latest twrp for the android device using the codename.
× /orangefox `<codename>`:  Gets latest orangefox recovery for the android device using the codename.
× /los `<codename>`: Gets Latest lineage os build.
"""

__mod_name__ = "Android"

MAGISK_HANDLER = DisableAbleCommandHandler("magisk", magisk, run_async=True)
TWRP_HANDLER = DisableAbleCommandHandler("twrp", twrp, pass_args=True, run_async=True)
DEVICE_HANDLER = DisableAbleCommandHandler(
    "device", device, pass_args=True, run_async=True
)
ORANGEFOX_HANDLER = DisableAbleCommandHandler(
    "orangefox", orangefox, pass_args=True, run_async=True
)
LOS_HANDLER = DisableAbleCommandHandler("los", los, pass_args=True, run_async=True)
BOOTLEG_HANDLER = DisableAbleCommandHandler(
    "bootleg", bootleg, pass_args=True, run_async=True
)
GSI_HANDLER = DisableAbleCommandHandler("gsi", gsi, pass_args=True, run_async=True)

dispatcher.add_handler(MAGISK_HANDLER)
dispatcher.add_handler(TWRP_HANDLER)
dispatcher.add_handler(DEVICE_HANDLER)
dispatcher.add_handler(ORANGEFOX_HANDLER)
dispatcher.add_handler(LOS_HANDLER)
dispatcher.add_handler(GSI_HANDLER)
dispatcher.add_handler(BOOTLEG_HANDLER)
