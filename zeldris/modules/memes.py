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


import random
import re
import time

import requests as r
from telegram import MAX_MESSAGE_LENGTH, ParseMode, TelegramError, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown

import zeldris.modules.helper_funcs.fun_strings as fun
from zeldris import LOGGER, DEV_USERS, SUPPORT_USERS, dispatcher
from zeldris.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.extraction import extract_user
from zeldris.modules.helper_funcs.filters import CustomFilters


@typing_action
def runs(update: Update, _: CallbackContext):
    update.effective_message.reply_text(random.choice(fun.RUN_STRINGS))


@typing_action
def slap(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message

    # reply to correct message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id
        )

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                slapped_user.first_name, slapped_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(fun.SLAP_TEMPLATES)
    item = random.choice(fun.ITEMS)
    hit = random.choice(fun.HIT)
    throw = random.choice(fun.THROW)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@typing_action
def punch(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message

    # reply to correct message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id
        )

    user_id = extract_user(update.effective_message, args)
    if user_id:
        punched_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if punched_user.username:
            user2 = "@" + escape_markdown(punched_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                punched_user.first_name, punched_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(fun.PUNCH_TEMPLATES)
    item = random.choice(fun.ITEMS)
    punches = random.choice(fun.PUNCH)

    repl = temp.format(user1=user1, user2=user2, item=item, punches=punches)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@typing_action
def police(update: Update, _: CallbackContext):
    message = update.effective_message.reply_text("Wuanjayy...")
    for i in fun.POLICE:
        message.edit_text(i)
        time.sleep(0.5)


@typing_action
def hug(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message

    # reply to correct message
    reply_text = (
        msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text
    )

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id
        )

    user_id = extract_user(update.effective_message, args)
    if user_id:
        hugged_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if hugged_user.username:
            user2 = "@" + escape_markdown(hugged_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                hugged_user.first_name, hugged_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "Awwh! [{}](tg://user?id={})".format(
            context.bot.first_name, context.bot.id
        )
        user2 = curr_user

    temp = random.choice(fun.HUG_TEMPLATES)
    hugs = random.choice(fun.HUG)

    repl = temp.format(user1=user1, user2=user2, hug=hugs)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@typing_action
def abuse(update: Update, _: CallbackContext):
    # reply to correct message
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.ABUSE_STRINGS))


@typing_action
def dice(update: Update, context: CallbackContext):
    context.bot.sendDice(update.effective_chat.id)


@typing_action
def shrug(update: Update, _: CallbackContext):
    # reply to correct message
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.SHGS))


# def decide(update: Update, context: CallbackContext):
#    args = update.effective_message.text.split(None, 1)
#    if len(args) >= 2:  # Don't reply if no args
#        reply_text = (
#            update.effective_message.reply_to_message.reply_text
#            if update.effective_message.reply_to_message
#            else update.effective_message.reply_text
#        )
#        reply_text(random.choice(fun.DECIDE))


def yesnowtf(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    res = r.get("https://yesno.wtf/api")
    if res.status_code != 200:
        return msg.reply_text(random.choice(fun.DECIDE))
    res = res.json()
    try:
        context.bot.send_animation(
            chat.id, animation=res["image"], caption=str(res["answer"]).upper()
        )
    except BadRequest:
        return


@typing_action
def table(update: Update, _: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.TABLE))


@typing_action
def cri(update: Update, _: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.CRI))


@typing_action
def recite(update: Update, _: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.BEING_LOGICAL))


@typing_action
def gbun(update: Update, context: CallbackContext):
    user = update.effective_user
    chat = update.effective_chat

    if update.effective_message.chat.type == "private":
        return
    if int(user.id) in DEV_USERS or int(user.id) in SUPPORT_USERS:
        context.bot.sendMessage(chat.id, (random.choice(fun.GBUN)))


@typing_action
def snipe(update: Update, context: CallbackContext):
    args = context.args
    try:
        chat_id = str(args[0])
        del args[0]
    except (TypeError, IndexError):
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            context.bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text(
                "Couldn't send the message. Perhaps I'm not part of that group?"
            )
    else:
        update.effective_message.reply_text(
            "Where should i send??\nGive me the chat id!"
        )


@typing_action
def copypasta(update: Update, _: CallbackContext):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to make pasta.")
    else:
        emojis = [
            "😂",
            "😂",
            "👌",
            "✌",
            "💞",
            "👍",
            "👌",
            "💯",
            "🎶",
            "👀",
            "😂",
            "👓",
            "👏",
            "👐",
            "🍕",
            "💥",
            "🍴",
            "💦",
            "💦",
            "🍑",
            "🍆",
            "😩",
            "😏",
            "👉👌",
            "👀",
            "👅",
            "😩",
            "🚰",
        ]
        reply_text = random.choice(emojis)
        # choose a random character in the message to be substituted with 🅱️
        b_char = random.choice(message.reply_to_message.text).lower()
        for c in message.reply_to_message.text:
            if c == " ":
                reply_text += random.choice(emojis)
            elif c in emojis:
                reply_text += c
                reply_text += random.choice(emojis)
            elif c.lower() == b_char:
                reply_text += "🅱️"
            else:
                reply_text += c.upper() if bool(random.getrandbits(1)) else c.lower()
        reply_text += random.choice(emojis)
        message.reply_to_message.reply_text(reply_text)


@typing_action
def clapmoji(update: Update, _: CallbackContext):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to clap!")
    else:
        reply_text = "👏 "
        reply_text += message.reply_to_message.text.replace(" ", " 👏 ")
        reply_text += " 👏"
        message.reply_to_message.reply_text(reply_text)


@typing_action
def owo(update: Update, _: CallbackContext):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        faces = [
            "(・`ω´・)",
            ";;w;;",
            "owo",
            "UwU",
            ">w<",
            "^w^",
            r"\(^o\) (/o^)/",
            "( ^ _ ^)∠☆",
            "(ô_ô)",
            "~:o",
            ";____;",
            "(*^*)",
            "(>_",
            "(♥_♥)",
            "*(^O^)*",
            "((+_+))",
        ]
        re.sub(r"[rl]", "w", message.reply_to_message.text)
        reply_text = re.sub(r"[ｒｌ]", "ｗ", message.reply_to_message.text)
        reply_text = re.sub(r"[RL]", "W", reply_text)
        reply_text = re.sub(r"[ＲＬ]", "Ｗ", reply_text)
        reply_text = re.sub(r"n([aeiouａｅｉｏｕ])", r"ny\1", reply_text)
        reply_text = re.sub(r"ｎ([ａｅｉｏｕ])", r"ｎｙ\1", reply_text)
        reply_text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", reply_text)
        reply_text = re.sub(r"Ｎ([ａｅｉｏｕＡＥＩＯＵ])", r"Ｎｙ\1", reply_text)
        reply_text = re.sub(r"!+", " " + random.choice(faces), reply_text)
        reply_text = re.sub(r"！+", " " + random.choice(faces), reply_text)
        reply_text = reply_text.replace("ove", "uv")
        reply_text = reply_text.replace("ｏｖｅ", "ｕｖ")
        reply_text += " " + random.choice(faces)
        message.reply_to_message.reply_text(reply_text)


@typing_action
def stretch(update: Update, _: CallbackContext):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to streeeeeeeeetch.")
    else:
        count = random.randint(3, 10)
        reply_text = re.sub(
            r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])",
            (r"\1" * count),
            message.reply_to_message.text,
        )
        if len(reply_text) >= MAX_MESSAGE_LENGTH:
            return message.reply_text(
                "Result of this message was too long for telegram!"
            )

        message.reply_to_message.reply_text(reply_text)


def me_too(update: Update, _: CallbackContext):
    message = update.effective_message
    reply = random.choice(["Me too thanks", "Haha yes, me too", "Same lol", "Me irl"])
    message.reply_text(reply)


def goodnight(update: Update, _: CallbackContext):
    message = update.effective_message
    reply = random.choice(fun.GDNIGHT)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


def goodmorning(update: Update, _: CallbackContext):
    message = update.effective_message
    reply = random.choice(fun.GDMORNING)
    message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


__help__ = """
Some dank memes for fun or whatever!

× /shrug | /cri: Get shrug or ToT.
× /decide: Randomly answer yes no etc.
× /abuse: Abuses the retard!
× /table: Flips a table...
× /runs: Reply a random string from an array of replies.
× /slap: Slap a user, or get slapped if not a reply.
× /pasta: Famous copypasta meme, try and see.
× /clap: Claps on someones message!
× /owo: UwU-fy whole text XD.
× /roll: Rolls a dice.
× /recite: Logical quotes to change your life.
× /stretch:  streeeeeeetch iiiiiiit.
× /warm: Hug a user warmly, or get hugged if not a reply.
× /punch: Punch a user, or get punched if not a reply.
× /police: Give Police siren Animation.

*Regex based memes:*
`/decide` (disabled rn) can be also used with regex like: `zeldris What? <question>: randomly answer "Yes, No" etc.`
Some other regex filters are:
`me too` | `good morning` | `good night`.

Zeldris will reply random strings accordingly when these words are used!
All regex filters can be disabled incase u don't want... like: `/disable metoo`.
"""

__mod_name__ = "Memes"

SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug, run_async=True)
# DECIDE_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(zeldris)"), decide, friendly="decide", run_async=True)
SNIPE_HANDLER = CommandHandler(
    "snipe",
    snipe,
    pass_args=True,
    filters=CustomFilters.dev_filter,
    run_async=True,
)
ABUSE_HANDLER = DisableAbleCommandHandler("abuse", abuse, run_async=True)
POLICE_HANDLER = DisableAbleCommandHandler("police", police, run_async=True)
RUNS_HANDLER = DisableAbleCommandHandler("runs", runs, run_async=True)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True, run_async=True)
PUNCH_HANDLER = DisableAbleCommandHandler(
    "punch", punch, pass_args=True, run_async=True
)
HUG_HANDLER = DisableAbleCommandHandler("warm", hug, pass_args=True, run_async=True)
GBUN_HANDLER = CommandHandler("gbun", gbun, run_async=True)
TABLE_HANDLER = DisableAbleCommandHandler("table", table, run_async=True)
CRI_HANDLER = DisableAbleCommandHandler("cri", cri, run_async=True)
PASTA_HANDLER = DisableAbleCommandHandler("pasta", copypasta, run_async=True)
CLAP_HANDLER = DisableAbleCommandHandler("clap", clapmoji, run_async=True)
OWO_HANDLER = DisableAbleCommandHandler("owo", owo, run_async=True)
STRECH_HANDLER = DisableAbleCommandHandler("stretch", stretch, run_async=True)
MEETOO_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(me too)"), me_too, friendly="metoo", run_async=True
)
RECITE_HANDLER = DisableAbleCommandHandler("recite", recite, run_async=True)
DICE_HANDLER = DisableAbleCommandHandler("roll", dice, run_async=True)
YESNOWTF_HANDLER = DisableAbleCommandHandler("decide", yesnowtf, run_async=True)
GDMORNING_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(good morning)"),
    goodmorning,
    friendly="goodmorning",
    run_async=True,
)
GDNIGHT_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"(?i)(good night)"),
    goodnight,
    friendly="goodnight",
    run_async=True,
)

dispatcher.add_handler(POLICE_HANDLER)
dispatcher.add_handler(SHRUG_HANDLER)
# dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(ABUSE_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(HUG_HANDLER)
dispatcher.add_handler(GBUN_HANDLER)
dispatcher.add_handler(TABLE_HANDLER)
dispatcher.add_handler(RECITE_HANDLER)
dispatcher.add_handler(CRI_HANDLER)
dispatcher.add_handler(PASTA_HANDLER)
dispatcher.add_handler(CLAP_HANDLER)
dispatcher.add_handler(OWO_HANDLER)
dispatcher.add_handler(STRECH_HANDLER)
dispatcher.add_handler(MEETOO_HANDLER)
dispatcher.add_handler(DICE_HANDLER)
dispatcher.add_handler(YESNOWTF_HANDLER)
dispatcher.add_handler(GDMORNING_HANDLER)
dispatcher.add_handler(GDNIGHT_HANDLER)
