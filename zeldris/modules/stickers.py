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


import math
import os
from html import escape

import requests
from PIL import Image
from bs4 import BeautifulSoup
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram import TelegramError
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from zeldris import dispatcher
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action

combot_stickers_url = "https://combot.org/telegram/stickers?q="


@typing_action
def combot_sticker(update: Update, _: CallbackContext):
    msg = update.effective_message
    split = msg.text.split(" ", 1)
    if len(split) == 1:
        msg.reply_text("Provide Some Name To Search For Packs.")
        return
    text = requests.get(combot_stickers_url + split[1]).text
    soup = BeautifulSoup(text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        msg.reply_text("No Results Found! :(")
        return
    reply = f"Stickers for *{split[1]}*:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\n• [{title.get_text()}]({link})"
    msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


@typing_action
def kang(update: Update, context: CallbackContext):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = (
                    "a"
                    + str(packnum)
                    + "_"
                    + str(user.id)
                    + "_by_"
                    + context.bot.username
                )
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1
    is_animated = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yea, I can't kang that.")

        kang_file = context.bot.get_file(file_id)
        if not is_animated:
            kang_file.download("kangsticker.png")
        else:
            kang_file.download("kangsticker.tgs")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        if not is_animated:
            kangsticker = "kangsticker.png"
            try:
                im = Image.open(kangsticker)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    maxsize = (512, 512)
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(kangsticker, "PNG")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                msg.reply_text(
                    f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                    + f"\nEmoji is: {sticker_emoji}",
                    parse_mode=ParseMode.MARKDOWN,
                )

            except OSError as e:
                msg.reply_text("I can only kang images m8.")
                print(e)
                return

            except TelegramError as e:
                if e.message == "Internal Server Error: sticker set not found (500)":
                    msg.reply_text(
                        "Sticker successfully added to [pack](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "Emoji is:" + " " + sticker_emoji,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        png_sticker=open("kangsticker.png", "rb"),
                        emojis=sticker_emoji,
                    )
                    msg.reply_text(
                        f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                        + f"\nEmoji is: {sticker_emoji}",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif e.message == "Stickers_too_much":
                    msg.reply_text("Max packsize reached. Press F to pay respecc.")
                elif e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open("kangsticker.png", "rb"),
                    )
                print(e)

        else:
            packname = "animated" + str(user.id) + "_by_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    stickerset = context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "animated"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_by_"
                            + context.bot.username
                        )
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open("kangsticker.tgs", "rb"),
                    emojis=sticker_emoji,
                )
                msg.reply_text(
                    f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
                    + f"\nEmoji is: {sticker_emoji}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except TelegramError as e:
                if e.message == "Internal Server Error: sticker set not found (500)":
                    msg.reply_text(
                        "Sticker successfully added to [pack](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "Emoji is:" + " " + sticker_emoji,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        tgs_sticker=open("kangsticker.tgs", "rb"),
                    )
                print(e)

    else:
        packs = "Please reply to a sticker, or image to kang it!\nOh, by the way. here are your packs:\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + "_by_" + context.bot.username
            for i in range(packnum + 1):
                if i == 0:
                    packs += f"[pack](t.me/addstickers/{firstpackname})\n"
                else:
                    packs += f"[pack{i}](t.me/addstickers/{packname})\n"
        else:
            packs += f"[pack](t.me/addstickers/{packname})"
        msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)
    if os.path.isfile("kangsticker.png"):
        os.remove("kangsticker.png")
    elif os.path.isfile("kangsticker.tgs"):
        os.remove("kangsticker.tgs")


def makepack_internal(
    _,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
):
    name = user.first_name
    name = name[:50]
    try:
        extra_version = " " + str(packnum) if packnum > 0 else ""
        if png_sticker:
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s kang pack" + extra_version,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s animated kang pack" + extra_version,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )

    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            msg.reply_text(
                "Your pack can be found [here](t.me/addstickers/%s)" % packname,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg.reply_text(
                "Contact me in PM first.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Start", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        return

    if success:
        msg.reply_text(
            "Sticker pack successfully created. Get it [here](t.me/addstickers/%s)"
            % packname,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")


def getsticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        context.bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text(
            "Hello"
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please check the file you requested below."
            "\nPlease use this feature wisely!",
            parse_mode=ParseMode.HTML,
        )
        context.bot.sendChatAction(chat_id, "upload_document")
        file_id = msg.reply_to_message.sticker.file_id
        new_file = context.bot.get_file(file_id)
        new_file.download("sticker.png")
        context.bot.sendDocument(chat_id, document=open("sticker.png", "rb"))
        context.bot.sendChatAction(chat_id, "upload_photo")
        context.bot.send_photo(chat_id, photo=open("sticker.png", "rb"))

    else:
        context.bot.sendChatAction(chat_id, "typing")
        update.effective_message.reply_text(
            "Hello"
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get sticker image",
            parse_mode=ParseMode.HTML,
        )


@typing_action
def stickerid(update: Update, _: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            parse_mode=ParseMode.HTML,
        )


__help__ = """
Kanging Stickers made easy with stickers module!

× /stickers: Find stickers for given term on combot sticker catalogue.
× /stickerid: Reply to a sticker to me to tell you its file ID.
× /getsticker: Reply to a sticker to me to upload its raw PNG file.
× /kang: Reply to a sticker to add it to your pack.
"""

__mod_name__ = "Stickers"
KANG_HANDLER = DisableAbleCommandHandler(
    ["kang", "steal"],
    kang,
    pass_args=True,
    run_async=True,
)
STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, run_async=True)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, run_async=True)
FIND_STICKERS_HANDLER = DisableAbleCommandHandler(
    "stickers", combot_sticker, run_async=True
)


dispatcher.add_handler(KANG_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
dispatcher.add_handler(FIND_STICKERS_HANDLER)
