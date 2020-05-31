import random, re
import requests as r

from time import sleep
from typing import Optional, List
from random import randint

from telegram import Message, Update, Bot, User, ParseMode, MessageEntity, MAX_MESSAGE_LENGTH
from telegram.ext import Filters, CommandHandler, MessageHandler, run_async
from telegram import TelegramError, Chat, Message
from telegram.error import BadRequest
from telegram.utils.helpers import mention_html, escape_markdown

from skylee.modules.helper_funcs.extraction import extract_user
from skylee.modules.helper_funcs.filters import CustomFilters
from skylee.modules.helper_funcs.alternate import typing_action
from skylee import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WALL_API, TOKEN
from skylee.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler

import skylee.modules.helper_funcs.fun_strings as fun

@run_async
@typing_action
def runs(update, context):
    update.effective_message.reply_text(random.choice(fun.RUN_STRINGS))


@run_async
@typing_action
def slap(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

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


@run_async
@typing_action
def punch(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        punched_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if punched_user.username:
            user2 = "@" + escape_markdown(punched_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(punched_user.first_name,
                                                   punched_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(fun.PUNCH_TEMPLATES)
    item = random.choice(fun.ITEMS)
    punch = random.choice(fun.PUNCH)

    repl = temp.format(user1=user1, user2=user2, item=item, punches=punch)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)



@run_async
@typing_action
def hug(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        hugged_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if hugged_user.username:
            user2 = "@" + escape_markdown(hugged_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(hugged_user.first_name,
                                                   hugged_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "Awwh! [{}](tg://user?id={})".format(context.bot.first_name, context.bot.id)
        user2 = curr_user

    temp = random.choice(fun.HUG_TEMPLATES)
    hug = random.choice(fun.HUG)

    repl = temp.format(user1=user1, user2=user2, hug=hug)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
@typing_action
def abuse(update, context):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun.ABUSE_STRINGS))

@run_async
@typing_action
def dice(update, context):
    context.bot.sendDice(update.effective_chat.id)

@run_async
@typing_action
def shrug(update, context):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun.SHGS))

@run_async
def decide(update, context):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2: # Don't reply if no args
       reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
       reply_text(random.choice(fun.DECIDE))

@run_async
def yesnowtf(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    res = r.get("https://yesno.wtf/api")
    if res.status_code != 200:
       return msg.reply_text(random.choice(fun.DECIDE))
    else:
       res = res.json()
    try:
       context.bot.send_animation(chat.id,
       animation=res["image"],
       caption=str(res["answer"]).upper())
    except BadRequest:
           return

@run_async
@typing_action
def table(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun.TABLE))

@run_async
@typing_action
def cri(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun.CRI))

@run_async
@typing_action
def recite(update, context):
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(fun.BEING_LOGICAL))

@run_async
@typing_action
def gbun(update, context):
    user = update.effective_user
    chat = update.effective_chat

    if update.effective_message.chat.type == "private":
       return
    if int(user.id) in SUDO_USERS or int(user.id) in SUPPORT_USERS:
       context.bot.sendMessage(chat.id, (random.choice(fun.GBUN)))

@run_async
@typing_action
def snipe(update, context):
    args = context.args
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")     
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            context.bot.sendMessage(int(chat_id), str(to_send))        
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))             
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")


@run_async
@typing_action
def copypasta(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to make pasta.")
    else:
        emojis = ["😂", "😂", "👌", "✌", "💞", "👍", "👌", "💯", "🎶", "👀", "😂", "👓", "👏", "👐", "🍕", "💥", "🍴", "💦", "💦", "🍑", "🍆", "😩", "😏", "👉👌", "👀", "👅", "😩", "🚰"]
        reply_text = random.choice(emojis)
        b_char = random.choice(message.reply_to_message.text).lower() # choose a random character in the message to be substituted with 🅱️
        for c in message.reply_to_message.text:
            if c == " ":
                reply_text += random.choice(emojis)
            elif c in emojis:
                reply_text += c
                reply_text += random.choice(emojis)
            elif c.lower() == b_char:
                reply_text += "🅱️"
            else:
                if bool(random.getrandbits(1)):
                    reply_text += c.upper()
                else:
                    reply_text += c.lower()
        reply_text += random.choice(emojis)
        message.reply_to_message.reply_text(reply_text)


@run_async
@typing_action
def clapmoji(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to clap!")
    else:
        reply_text = "👏 "
        reply_text += message.reply_to_message.text.replace(" ", " 👏 ")
        reply_text += " 👏"
        message.reply_to_message.reply_text(reply_text)


@run_async
@typing_action
def owo(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to meme.")
    else:
        faces = ['(・`ω´・)',';;w;;','owo','UwU','>w<','^w^','\(^o\) (/o^)/','( ^ _ ^)∠☆','(ô_ô)','~:o',';____;', '(*^*)', '(>_', '(♥_♥)', '*(^O^)*', '((+_+))']
        reply_text = re.sub(r'[rl]', "w", message.reply_to_message.text)
        reply_text = re.sub(r'[ｒｌ]', "ｗ", message.reply_to_message.text)
        reply_text = re.sub(r'[RL]', 'W', reply_text)
        reply_text = re.sub(r'[ＲＬ]', 'Ｗ', reply_text)
        reply_text = re.sub(r'n([aeiouａｅｉｏｕ])', r'ny\1', reply_text)
        reply_text = re.sub(r'ｎ([ａｅｉｏｕ])', r'ｎｙ\1', reply_text)
        reply_text = re.sub(r'N([aeiouAEIOU])', r'Ny\1', reply_text)
        reply_text = re.sub(r'Ｎ([ａｅｉｏｕＡＥＩＯＵ])', r'Ｎｙ\1', reply_text)
        reply_text = re.sub(r'\!+', ' ' + random.choice(faces), reply_text)
        reply_text = re.sub(r'！+', ' ' + random.choice(faces), reply_text)
        reply_text = reply_text.replace("ove", "uv")
        reply_text = reply_text.replace("ｏｖｅ", "ｕｖ")
        reply_text += ' ' + random.choice(faces)
        message.reply_to_message.reply_text(reply_text)


@run_async
@typing_action
def stretch(update, context):
    message = update.effective_message
    if not message.reply_to_message:
        message.reply_text("I need a message to streeeeeeeeetch.")
    else:
        count = random.randint(3, 10)
        reply_text = re.sub(r'([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])', (r'\1' * count), message.reply_to_message.text)
        if len(reply_text) >= MAX_MESSAGE_LENGTH:
           return message.reply_text("Result of this message was too long for telegram!")

        message.reply_to_message.reply_text(reply_text)


@run_async
def me_too(update, context):
    message = update.effective_message
    reply = random.choice(["Me too thanks", "Haha yes, me too", "Same lol", "Me irl"])
    message.reply_text(reply)

@run_async
def goodnight(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDNIGHT)
    message.reply_text(reply,
    parse_mode=ParseMode.MARKDOWN)

@run_async
def goodmorning(update, context):
    message = update.effective_message
    reply = random.choice(fun.GDMORNING)
    message.reply_text(reply,
    parse_mode=ParseMode.MARKDOWN)


# Bug reporting module for X00TD PORTS!

@run_async
def ports_bug(update, context):
    message = update.effective_message
    user = update.effective_user
    bug = message.text[len('/bug '):]
    chat = update.effective_chat

    PORT_GRP = [-1001297379754, -1001469684768]

    if not int(chat.id) in PORT_GRP:
        return

    if not bug:
        message.reply_text("Submitting empty bug report won't do anything!")
        return

    if bug:
        context.bot.sendMessage(-1001495581911, "<b>NEW BUG REPORT!</b>\n\n<b>Submitted by</b>: {}.\n\nDescription: <code>{}</code>.".format(
                                mention_html(user.id, user.first_name), bug), parse_mode=ParseMode.HTML)
        message.reply_text("Successfully submitted bug report!")


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

*Regex based memes:*

`/decide` can be also used with regex like: `skylee? <question>: randomly answer "Yes, No" etc.`

Some other regex filters are:
`me too` | `goodmorning` | `goodnight`.

Skylee will reply random strings accordingly when these words are used!
All regex filters can be disabled incase u don't want... like: `/disable metoo`.

"""

__mod_name__ = "Memes"

SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug)
DECIDE_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)^skylee\?"), decide, friendly="decide")
SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
ABUSE_HANDLER = DisableAbleCommandHandler("abuse", abuse)
PORT_BUG_HANDLER = CommandHandler("bug", ports_bug)
RUNS_HANDLER = DisableAbleCommandHandler("runs", runs)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
PUNCH_HANDLER = DisableAbleCommandHandler("punch", punch, pass_args=True)
HUG_HANDLER = DisableAbleCommandHandler("warm", hug, pass_args=True)
GBUN_HANDLER = CommandHandler("gbun", gbun)
TABLE_HANDLER = DisableAbleCommandHandler("table", table)
CRI_HANDLER = DisableAbleCommandHandler("cri", cri)
PASTA_HANDLER = DisableAbleCommandHandler("pasta", copypasta)
CLAP_HANDLER = DisableAbleCommandHandler("clap", clapmoji)
OWO_HANDLER = DisableAbleCommandHandler("owo", owo)
STRECH_HANDLER = DisableAbleCommandHandler("stretch", stretch)
MEETOO_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(me too)"), me_too, friendly="metoo")
RECITE_HANDLER = DisableAbleCommandHandler("recite", recite)
DICE_HANDLER = DisableAbleCommandHandler("roll", dice)
YESNOWTF_HANDLER = DisableAbleCommandHandler("decide", yesnowtf)
GDMORNING_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodmorning)"), goodmorning, friendly="goodmorning")
GDNIGHT_HANDLER = DisableAbleMessageHandler(Filters.regex(r"(?i)(goodnight)"), goodnight, friendly="goodnight")


dispatcher.add_handler(SHRUG_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(ABUSE_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(PORT_BUG_HANDLER)
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
