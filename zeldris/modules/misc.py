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


import codecs
import html
import os
import random
import re
from io import BytesIO
from random import randint
from typing import Optional

import requests
import wikipedia
from requests import get
from telegram import (
    Message,
    Chat,
    MessageEntity,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ParseMode,
    ChatAction,
    TelegramError,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import escape_markdown, mention_html

from zeldris import (
    dispatcher,
    OWNER_ID,
    DEV_USERS,
    SUPPORT_USERS,
    WHITELIST_USERS,
    WALL_API,
    spamwtc,
)
from zeldris.__main__ import STATS, USER_INFO, GDPR
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action, send_action
from zeldris.modules.helper_funcs.extraction import extract_user
from zeldris.modules.helper_funcs.filters import CustomFilters


@typing_action
def get_id(update: Update, context: CallbackContext):
    args = context.args
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if (
            update.effective_message.reply_to_message
            and update.effective_message.reply_to_message.forward_from
        ):
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id,
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            user = context.bot.get_chat(user_id)
            update.effective_message.reply_text(
                "{}'s id is `{}`.".format(escape_markdown(user.first_name), user.id),
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text(
                "Your id is `{}`.".format(chat.id), parse_mode=ParseMode.MARKDOWN
            )

        else:
            update.effective_message.reply_text(
                "This group's id is `{}`.".format(chat.id),
                parse_mode=ParseMode.MARKDOWN,
            )


def info(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)
    chat = update.effective_chat

    if user_id:
        user = context.bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].isdigit()
            and not msg.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        msg.reply_text("I can't extract a user from this.")
        return

    else:
        return

    del_msg = msg.reply_text(
        "Hold tight while I steal some data from <b>FBI Database</b>...",
        parse_mode=ParseMode.HTML,
    )

    text = (
        "<b>USER INFO</b>:"
        "\n\nID: <code>{}</code>"
        "\nFirst Name: {}".format(user.id, html.escape(user.first_name))
    )

    if user.last_name:
        text += "\nLast Name: {}".format(html.escape(user.last_name))

    if user.username:
        text += "\nUsername: @{}".format(html.escape(user.username))

    text += "\nPermanent user link: {}".format(mention_html(user.id, "link"))

    text += "\nNumber of profile pics: {}".format(
        context.bot.get_user_profile_photos(user.id).total_count
    )

    try:
        sw = spamwtc.get_ban(int(user.id))
        if sw:
            text += "\n\n<b>This person is banned in Spamwatch!</b>"
            text += f"\nResason: <pre>{sw.reason}</pre>"
    except BaseException:
        pass  # Don't break on exceptions like if api is down?

    if user.id == OWNER_ID:
        text += "\n\nAye this guy is my owner.\nI would never do anything against him!"

    elif user.id in DEV_USERS:
        text += (
            "\n\nThis person is one of my dev users! "
            "Nearly as powerful as my owner - so watch it."
        )

    elif user.id in SUPPORT_USERS:
        text += (
            "\n\nThis person is one of my support users! "
            "Not quite a sudo user, but can still gban you off the map."
        )

    elif user.id in WHITELIST_USERS:
        text += (
            "\n\nThis person has been whitelisted! "
            "That means I'm not allowed to ban/kick them."
        )

    try:
        memstatus = chat.get_member(user.id).status
        if memstatus in ["administrator", "creator"]:
            result = context.bot.get_chat_member(chat.id, user.id)
            if result.custom_title:
                text += f"\n\nThis user has custom title <b>{result.custom_title}</b> in this chat."
    except BadRequest:
        pass

    for mod in USER_INFO:
        try:
            mod_info = mod.__user_info__(user.id).strip()
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    try:
        profile = context.bot.get_user_profile_photos(user.id).photos[0][-1]
        context.bot.sendChatAction(chat.id, "upload_photo")
        context.bot.send_photo(
            chat.id,
            photo=profile,
            caption=text,
            parse_mode=ParseMode.HTML,
        )
    except IndexError:
        context.bot.sendChatAction(chat.id, "typing")
        msg.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    finally:
        del_msg.delete()


@typing_action
def echo(update, _):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    message.delete()


@typing_action
def gdpr(update, _):
    update.effective_message.reply_text("Deleting identifiable data...")
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text(
        "Your personal data has been deleted.\n\nNote that this will not unban "
        "you from any chats, as that is telegram data, not Skylee data. "
        "Flooding, warns, and gbans are also preserved, as of "
        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual"
        "-rights/right-to-erasure/), "
        "which clearly states that the right to erasure does not apply "
        '"for the performance of a task carried out in the public interest", as is '
        "the case for the aforementioned pieces of data.",
        parse_mode=ParseMode.MARKDOWN,
    )


MARKDOWN_HELP = """
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>~strike~</code> wrapping text with '~' will produce strikethrough text
- <code>--underline--</code> wrapping text with '--' will produce underline text
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""".format(
    dispatcher.bot.first_name
)


@typing_action
def markdown_help(update, _):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, --underline--, *bold*, `code`, ~strike~ "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


@typing_action
def wiki(update: Update, context: CallbackContext):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if not str(kueri[1]):
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔧 More Info...", url=wikipedia.page(kueri).url
                        )
                    ]
                ]
            )
            context.bot.editMessageText(
                chat_id=update.effective_chat.id,
                message_id=pertama.message_id,
                text=wikipedia.summary(kueri, sentences=10),
                reply_markup=keyboard,
            )
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et:
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(
                f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}"
            )


@typing_action
def ud(update: Update, context: CallbackContext):
    msg = update.effective_message
    args = context.args
    text = " ".join(args).lower()
    if not text:
        msg.reply_text("Please enter keywords to search!")
        return
    if text == "starry":
        msg.reply_text("Fek off bitch!")
        return
    try:
        results = get(f"http://api.urbandictionary.com/v0/define?term={text}").json()
        reply_text = f'Word: {text}\nDefinition: {results["list"][0]["definition"]}'
        reply_text += f'\n\nExample: {results["list"][0]["example"]}'
    except IndexError:
        reply_text = (
            f"Word: {text}\nResults: Sorry could not find any matching results!"
        )
    ignore_chars = "[]"
    reply = reply_text
    for chars in ignore_chars:
        reply = reply.replace(chars, "")
    if len(reply) >= 4096:
        reply = reply[:4096]  # max msg lenth of tg.
    try:
        msg.reply_text(reply)
    except BadRequest as err:
        msg.reply_text(f"Error! {err.message}")


@typing_action
def src(update, _) -> None:
    update.effective_message.reply_text(
        "Hey there! You can find what makes me by clicking the button below!",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="GitHub repo",
                        url="github.com/IDN-C-X/ZeldrisRobot",
                    ),
                ],
            ],
            disable_web_page_preview=True,
        ),
    )


@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    caption = query
    term = query.replace(" ", "%20")
    json_rep = requests.get(
        f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}"
    ).json()
    if not json_rep.get("success"):
        msg.reply_text("An error occurred!")

    else:
        wallpapers = json_rep.get("wallpapers")
        if not wallpapers:
            msg.reply_text("No results found! Refine your search.")
            return
        index = randint(0, len(wallpapers) - 1)  # Choose random index
        wallpaper = wallpapers[index]
        wallpaper = wallpaper.get("url_image")
        wallpaper = wallpaper.replace("\\", "")
        context.bot.send_photo(
            chat_id,
            photo=wallpaper,
            caption="Preview",
            reply_to_message_id=msg_id,
            timeout=60,
        )
        context.bot.send_document(
            chat_id,
            document=wallpaper,
            filename="wallpaper",
            caption=caption,
            reply_to_message_id=msg_id,
            timeout=60,
        )


@typing_action
def getlink(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message
    if args:
        pattern = re.compile(r"-\d+")
    else:
        message.reply_text("You don't seem to be referring to any chats.")
    links = "Invite link(s):\n"
    for chat_id in pattern.findall(message.text):
        try:
            chat = context.bot.getChat(chat_id)
            bot_member = chat.get_member(context.bot.id)
            if bot_member.can_invite_users:
                invitelink = context.bot.exportChatInviteLink(chat_id)
                links += str(chat_id) + ":\n" + invitelink + "\n"
            else:
                links += (
                    str(chat_id) + ":\nI don't have access to the invite link." + "\n"
                )
        except BadRequest as excp:
            links += str(chat_id) + ":\n" + excp.message + "\n"
        except TelegramError as excp:
            links += str(chat_id) + ":\n" + excp.message + "\n"

    message.reply_text(links)


@send_action(ChatAction.UPLOAD_PHOTO)
def rmemes(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "meirl",
        "dankmemes",
        "AdviceAnimals",
        "memes",
        "meme",
        "memes_of_the_dank",
        "PornhubComments",
        "teenagers",
        "memesIRL",
        "insanepeoplefacebook",
        "terriblefacebookmemes",
    ]

    subreddit = random.choice(SUBREDS)
    res = requests.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        msg.reply_text("Sorry some error occurred :(")
        return
    res = res.json()

    rpage = res.get(str("subreddit"))  # Subreddit
    title = res.get(str("title"))  # Post title
    memeu = res.get(str("url"))  # meme pic url
    plink = res.get(str("postLink"))

    caps = f"× <b>Title</b>: {title}\n"
    caps += f"× <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(text="Subreddit Postlink 🔗", url=plink)]]
    try:
        context.bot.send_photo(
            chat.id,
            photo=memeu,
            caption=caps,
            reply_markup=InlineKeyboardMarkup(keyb),
            timeout=60,
            parse_mode=ParseMode.HTML,
        )

    except BadRequest as excp:
        return msg.reply_text(f"Error! {excp.message}")


def staff_ids(update, _):
    sfile = "List of SUDO & SUPPORT users:\n"
    sfile += f"× SUDO USER IDs; {DEV_USERS}\n"
    sfile += f"× SUPPORT USER IDs; {SUPPORT_USERS}"
    with BytesIO(str.encode(sfile)) as output:
        output.name = "staff-ids.txt"
        update.effective_message.reply_document(
            document=output,
            filename="staff-ids.txt",
            caption="Here is the list of SUDO & SUPPORTS users.",
        )


def stats(update, _):
    update.effective_message.reply_text(
        "Current stats:\n" + "\n".join([mod.__stats__() for mod in STATS])
    )


def paste(update: Update, context: CallbackContext):
    msg = update.effective_message

    if msg.reply_to_message and msg.reply_to_message.document:
        file = context.bot.get_file(msg.reply_to_message.document)
        file.download("file.txt")
        text = codecs.open("file.txt", "r+", encoding="utf-8")
        paste_text = text.read()
        url = "https://www.toptal.com/developers/hastebin/documents"
        key = requests.post(url, data=paste_text.encode("UTF-8")).json().get("key")
        text = "**Pasted to Hastebin!!!**"
        buttons = [
            [
                InlineKeyboardButton(
                    text="View Link",
                    url=f"https://www.toptal.com/developers/hastebin/{key}",
                ),
                InlineKeyboardButton(
                    text="View Raw",
                    url=f"https://www.toptal.com/developers/hastebin/raw/{key}",
                ),
            ]
        ]
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        os.remove("file.txt")
    else:
        msg.reply_text("Give me a text file to paste on hastebin")
        return


# /ip is for private use
__help__ = """
An "odds and ends" module for small, simple commands which don't really fit anywhere

× /id: Get the current group id. If used by replying to a message, gets that user's id.
× /info: Get information about a user.
× /wiki : Search wikipedia articles.
× /rmeme: Sends random meme scraped from reddit.
× /ud <query> : Search stuffs in urban dictionary.
× /wall <query> : Get random wallpapers directly from bot!
× /reverse : Reverse searches image or stickers on google.
× /paste: Saves replied content to `hastebin` and replies with a url.
× /gdpr: Deletes your information from the bot's database. Private chats only.
× /markdownhelp: Quick summary of how markdown works in telegram - can only be called in private chats.
"""

__mod_name__ = "Miscs"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True, run_async=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True, run_async=True)
ECHO_HANDLER = CommandHandler(
    "echo", echo, filters=CustomFilters.dev_filter, run_async=True
)
MD_HELP_HANDLER = CommandHandler(
    "markdownhelp", markdown_help, filters=Filters.chat_type.private, run_async=True
)
STATS_HANDLER = CommandHandler(
    "stats", stats, filters=Filters.user(DEV_USERS), run_async=True
)
GDPR_HANDLER = CommandHandler(
    "gdpr", gdpr, filters=Filters.chat_type.private, run_async=True
)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki, run_async=True)
WALLPAPER_HANDLER = DisableAbleCommandHandler(
    "wall", wall, pass_args=True, run_async=True
)
UD_HANDLER = DisableAbleCommandHandler("ud", ud, run_async=True)
GETLINK_HANDLER = CommandHandler(
    "getlink", getlink, pass_args=True, filters=Filters.user(DEV_USERS), run_async=True
)
STAFFLIST_HANDLER = CommandHandler(
    "staffids", staff_ids, filters=Filters.user(DEV_USERS), run_async=True
)
REDDIT_MEMES_HANDLER = DisableAbleCommandHandler("rmeme", rmemes, run_async=True)
SRC_HANDLER = CommandHandler(
    ["source", "repo"], src, filters=Filters.chat_type.groups, run_async=True
)
PASTE_HANDLER = DisableAbleCommandHandler("paste", paste, run_async=True)

dispatcher.add_handler(WALLPAPER_HANDLER)
dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(STAFFLIST_HANDLER)
dispatcher.add_handler(REDDIT_MEMES_HANDLER)
dispatcher.add_handler(SRC_HANDLER)
dispatcher.add_handler(PASTE_HANDLER)
