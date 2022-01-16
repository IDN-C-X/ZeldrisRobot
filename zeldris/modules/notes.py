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


import ast
import re
from html import escape
from io import BytesIO
from typing import Optional

from telegram import (
    MAX_MESSAGE_LENGTH,
    ParseMode,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from telegram import Message
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from telegram.utils.helpers import mention_html

import zeldris.modules.sql.notes_sql as sql
from zeldris import dispatcher, MESSAGE_DUMP, LOGGER
from zeldris.modules.connection import connected
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action
from zeldris.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from zeldris.modules.helper_funcs.misc import build_keyboard, revert_buttons
from zeldris.modules.helper_funcs.msg_types import get_note_type
from zeldris.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_to_html,
)

FILE_MATCHER = re.compile(r"^###file_id(!photo)?###:(.*?)(?:\s|$)")
STICKER_MATCHER = re.compile(r"^###sticker(!photo)?###:")
BUTTON_MATCHER = re.compile(r"^###button(!photo)?###:(.*?)(?:\s|$)")
MYFILE_MATCHER = re.compile(r"^###file(!photo)?###:")
MYPHOTO_MATCHER = re.compile(r"^###photo(!photo)?###:")
MYAUDIO_MATCHER = re.compile(r"^###audio(!photo)?###:")
MYVOICE_MATCHER = re.compile(r"^###voice(!photo)?###:")
MYVIDEO_MATCHER = re.compile(r"^###video(!photo)?###:")
MYVIDEONOTE_MATCHER = re.compile(r"^###video_note(!photo)?###:")

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}


# Do not async
def get(bot, update, notename, show_none=True, no_format=False):
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    user = update.effective_user
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        send_id = user.id
    else:
        chat_id = update.effective_chat.id
        send_id = chat_id

    note = sql.get_note(chat_id, notename)
    message = update.effective_message  # type: Optional[Message]

    if note:
        # If we're replying to a message, reply to that message (unless it's an error)
        if message.reply_to_message:
            reply_id = message.reply_to_message.message_id
        else:
            reply_id = message.message_id

        if note.is_reply:
            if MESSAGE_DUMP:
                try:
                    bot.forward_message(
                        chat_id=update.effective_chat.id,
                        from_chat_id=MESSAGE_DUMP,
                        message_id=note.value,
                    )
                except BadRequest as excp:
                    if excp.message != "Message to forward not found":
                        raise
                    message.reply_text(
                        "This message seems to have been lost - I'll remove it "
                        "from your notes list."
                    )
                    sql.rm_note(chat_id, notename)
            else:
                try:
                    bot.forward_message(
                        chat_id=update.effective_chat.id,
                        from_chat_id=chat_id,
                        message_id=note.value,
                    )
                except BadRequest as excp:
                    if excp.message != "Message to forward not found":
                        raise
                    message.reply_text(
                        "Looks like the original sender of this note has deleted "
                        "their message - sorry! Get your bot admin to start using a "
                        "message dump to avoid this. I'll remove this note from "
                        "your saved notes."
                    )
                    sql.rm_note(chat_id, notename)
        else:
            VALID_NOTE_FORMATTERS = [
                "first",
                "last",
                "fullname",
                "username",
                "id",
                "chatname",
                "mention",
            ]
            valid_format = escape_invalid_curly_brackets(
                note.value, VALID_NOTE_FORMATTERS
            )
            if valid_format:
                text = valid_format.format(
                    first=escape(message.from_user.first_name),
                    last=escape(
                        message.from_user.last_name or message.from_user.first_name
                    ),
                    fullname=" ".join(
                        [
                            escape(message.from_user.first_name),
                            escape(message.from_user.last_name),
                        ]
                        if message.from_user.last_name
                        else [escape(message.from_user.first_name)]
                    ),
                    username="@" + escape(message.from_user.username)
                    if message.from_user.username
                    else mention_html(
                        message.from_user.id, message.from_user.first_name
                    ),
                    mention=mention_html(
                        message.from_user.id, message.from_user.first_name
                    ),
                    chatname=escape(message.chat.title)
                    if message.chat.type != "private"
                    else escape(message.from_user.first_name),
                    id=message.from_user.id,
                )
            else:
                text = ""

            keyb = []
            parseMode = ParseMode.HTML
            buttons = sql.get_buttons(chat_id, notename)
            if no_format:
                parseMode = None
                text += revert_buttons(buttons)
            else:
                text = markdown_to_html(text)
                keyb = build_keyboard(buttons)

            keyboard = InlineKeyboardMarkup(keyb)

            try:
                if note.msgtype in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    bot.send_message(
                        update.effective_chat.id,
                        text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        reply_markup=keyboard,
                    )
                else:
                    ENUM_FUNC_MAP[note.msgtype](
                        update.effective_chat.id,
                        note.file,
                        caption=text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        reply_markup=keyboard,
                    )

            except BadRequest as excp:
                if excp.message == "Entity_mention_user_invalid":
                    message.reply_text(
                        "Looks like you tried to mention someone I've never seen before. If you really "
                        "want to mention them, forward one of their messages to me, and I'll be able "
                        "to tag them!"
                    )
                elif FILE_MATCHER.match(note.value):
                    message.reply_text(
                        "This note was an incorrectly imported file from another bot - I can't use "
                        "it. If you really need it, you'll have to save it again. In "
                        "the meantime, I'll remove it from your notes list."
                    )
                    sql.rm_note(chat_id, notename)
                else:
                    message.reply_text(
                        "This note could not be sent, as it is incorrectly formatted."
                    )

                    LOGGER.exception(
                        "Could not parse message #%s in chat %s", notename, str(chat_id)
                    )
                    LOGGER.warning("Message was: %s", str(note.value))
        return
    if show_none:
        message.reply_text("This note doesn't exist")


@typing_action
def cmd_get(update: Update, context: CallbackContext):
    args = context.args
    if len(args) >= 2 and args[1].lower() == "noformat":
        get(context.bot, update, args[0].lower(), show_none=True, no_format=True)
    elif len(args) >= 1:
        get(context.bot, update, args[0].lower(), show_none=True)
    else:
        update.effective_message.reply_text("Get rekt")


def hash_get(update: Update, context: CallbackContext):
    message = update.effective_message.text
    fst_word = message.split()[0]
    no_hash = fst_word[1:].lower()
    get(context.bot, update, no_hash, show_none=False)


@user_admin
@typing_action
def save(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        chat_name = "local notes" if chat.type == "private" else chat.title
    msg = update.effective_message

    note_name, text, data_type, content, buttons = get_note_type(msg)
    note_name = note_name.lower()

    if data_type is None:
        msg.reply_text("Bruh! there's no note")
        return

    if len(text.strip()) == 0:
        text = note_name

    sql.add_note_to_db(
        chat_id, note_name, text, data_type, buttons=buttons, file=content
    )

    msg.reply_text(
        "Saved '`{note_name}`' in *{chat_name}*.\nGet it with `/get {note_name}`, or `#{note_name}`!".format(
            note_name=note_name, chat_name=chat_name
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@user_admin
@typing_action
def clear(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    conn = connected(context.bot, update, chat, user.id)
    note_name, text, data_type, content, buttons = get_note_type(msg)

    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        chat_name = "local notes" if chat.type == "private" else chat.title
    if len(args) >= 1:
        notename = args[0].lower()

        if sql.rm_note(chat_id, notename):
            update.effective_message.reply_text(
                "Successfully deleted '`{note_name}`' from {chat_name}!".format(
                    note_name=note_name, chat_name=chat_name
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            update.effective_message.reply_text(
                "There is no such notes saved in {chat_name}!".format(
                    chat_name=chat_name
                )
            )


@typing_action
def list_notes(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    chat = update.effective_chat
    user = update.effective_user
    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
        msg = "*Notes in {}:*\n"
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = ""
            msg = "*Local Notes:*\n"
        else:
            chat_name = chat.title
            msg = "*Notes saved in {}:*\n"

    note_list = sql.get_all_chat_notes(chat_id)
    des = "You can get notes by using `/get notename`, or `#notename`.\n"
    for note in note_list:
        note_name = " × `{}`\n".format(note.name.lower())
        if len(msg) + len(note_name) > MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            msg = ""
        msg += note_name

    if not note_list:
        update.effective_message.reply_text("No notes saved here!")

    elif msg != "":
        try:
            update.effective_message.reply_text(
                msg.format(chat_name) + des, parse_mode=ParseMode.MARKDOWN
            )
        except ValueError:
            update.effective_message.reply_text(
                "There was a problem in showing notes list, maybe due to some invalid character in note names. Ask in "
                "@IDNCoderX if you're unable to figure it out! "
            )


@user_admin
def clear_notes(update, _):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    chatmem = chat.get_member(user.id)
    if chatmem.status == "creator":
        allnotes = sql.get_all_chat_notes(chat.id)
        if not allnotes:
            msg.reply_text("No notes saved here what should i delete?")
            return
        msg.reply_text(
            "Do you really wanna delete all of the notes??",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Yes I'm sure️", callback_data="rmnotes_true"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⚠️ Cancel", callback_data="rmnotes_cancel"
                        )
                    ],
                ]
            ),
        )

    else:
        msg.reply_text("This command can be only used by chat OWNER!")


@user_admin_no_reply
def rmbutton(update, _):
    query = update.callback_query
    userid = update.effective_user.id
    match = query.data.split("_")[1]
    chat = update.effective_chat

    usermem = chat.get_member(userid).status

    if match == "cancel" and usermem == "creator":
        return query.message.edit_text("Cancelled deletion of notes.")

    if match == "true" and usermem == "creator":

        allnotes = sql.get_all_chat_notes(chat.id)
        count = 0
        notelist = []
        for notename in allnotes:
            count += 1
            note = notename.name.lower()
            notelist.append(note)

        for i in notelist:
            sql.rm_note(chat.id, i)
        query.message.edit_text(f"Successfully cleaned {count} notes in {chat.title}.")


def __import_data__(chat_id, data):
    failures = []
    for notename, notedata in data.get("extra", {}).items():
        match = FILE_MATCHER.match(notedata)
        matchsticker = STICKER_MATCHER.match(notedata)
        matchbtn = BUTTON_MATCHER.match(notedata)
        matchfile = MYFILE_MATCHER.match(notedata)
        matchphoto = MYPHOTO_MATCHER.match(notedata)
        matchaudio = MYAUDIO_MATCHER.match(notedata)
        matchvoice = MYVOICE_MATCHER.match(notedata)
        matchvideo = MYVIDEO_MATCHER.match(notedata)
        matchvn = MYVIDEONOTE_MATCHER.match(notedata)

        if match:
            failures.append(notename)
            notedata = notedata[match.end() :].strip()
            if notedata:
                sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)
        elif matchsticker:
            content = notedata[matchsticker.end() :].strip()
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.STICKER, file=content
                )
        elif matchbtn:
            parse = notedata[matchbtn.end() :].strip()
            notedata = parse.split("<###button###>")[0]
            buttons = parse.split("<###button###>")[1]
            buttons = ast.literal_eval(buttons)
            if buttons:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.BUTTON_TEXT,
                    buttons=buttons,
                )
        elif matchfile:
            file = notedata[matchfile.end() :].strip()
            file = file.split("<###TYPESPLIT###>")
            notedata = file[1]
            content = file[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.DOCUMENT, file=content
                )
        elif matchphoto:
            photo = notedata[matchphoto.end() :].strip()
            photo = photo.split("<###TYPESPLIT###>")
            notedata = photo[1]
            content = photo[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.PHOTO, file=content
                )
        elif matchaudio:
            audio = notedata[matchaudio.end() :].strip()
            audio = audio.split("<###TYPESPLIT###>")
            notedata = audio[1]
            content = audio[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.AUDIO, file=content
                )
        elif matchvoice:
            voice = notedata[matchvoice.end() :].strip()
            voice = voice.split("<###TYPESPLIT###>")
            notedata = voice[1]
            content = voice[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VOICE, file=content
                )
        elif matchvideo:
            video = notedata[matchvideo.end() :].strip()
            video = video.split("<###TYPESPLIT###>")
            notedata = video[1]
            content = video[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VIDEO, file=content
                )
        elif matchvn:
            video_note = notedata[matchvn.end() :].strip()
            video_note = video_note.split("<###TYPESPLIT###>")
            notedata = video_note[1]
            content = video_note[0]
            if content:
                sql.add_note_to_db(
                    chat_id, notename[1:], notedata, sql.Types.VIDEO_NOTE, file=content
                )
        else:
            sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)

    if failures:
        with BytesIO(str.encode("\n".join(failures))) as output:
            output.name = "failed_imports.txt"
            dispatcher.bot.send_document(
                chat_id,
                document=output,
                filename="failed_imports.txt",
                caption="These files/photos failed to import due to originating "
                "from another bot. This is a telegram API restriction, and can't "
                "be avoided. Sorry for the inconvenience!",
            )


def __stats__():
    return "× {} notes, across {} chats.".format(sql.num_notes(), sql.num_chats())


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    notes = sql.get_all_chat_notes(chat_id)
    return "There are `{}` notes in this chat.".format(len(notes))


__help__ = """
Save data for future users with notes!

Notes are great to save random tidbits of information; a phone number, a nice gif, a funny picture - anything!

 × /get <notename>: Get the note with this notename
 × #<notename>: Same as /get
 × /notes or /saved: Lists all saved notes in the chat

If you would like to retrieve the contents of a note without any formatting, use `/get <notename> noformat`. This can \
be useful when updating a current note.

*Admin only:*
× /save <notename> <notedata>: Saves notedata as a note with name notename.
A button can be added to a note by using standard markdown link syntax - the link should just be prepended with a \
`buttonurl:` section, as such: `[somelink](buttonurl:example.com)`. Check /markdownhelp for more info.
× /save <notename>: Saves the replied message as a note with name notename.
× /clear <notename>: Clears note with this name.

*Chat creator only:*
× /rmallnotes: Clear all notes saved in chat at once.

 An example of how to save a note would be via:
`/save Data This is some data!`

Now, anyone using "/get notedata", or "#notedata" will be replied to with "This is some data!".

If you want to save an image, gif, or sticker, or any other data, do the following: `/save notename` while replying 
to a sticker or whatever data you'd like. Now, the note at "#notename" contains a sticker which will be sent as a 
reply. 

Tip: to retrieve a note without the formatting, use /get <notename> noformat This will retrieve the note and send it 
without formatting it; getting you the raw markdown, allowing you to make easy edits. 
"""

__mod_name__ = "Notes"

GET_HANDLER = DisableAbleCommandHandler("get", cmd_get, pass_args=True, run_async=True)
HASH_GET_HANDLER = MessageHandler(Filters.regex(r"^#[^\s]+"), hash_get, run_async=True)
SAVE_HANDLER = CommandHandler("save", save, run_async=True)
DELETE_HANDLER = CommandHandler("clear", clear, pass_args=True, run_async=True)
LIST_HANDLER = DisableAbleCommandHandler(
    ["notes", "saved"],
    list_notes,
    admin_ok=True,
    run_async=True,
)
CLEARALLNOTES_HANDLER = CommandHandler(
    "rmallnotes",
    clear_notes,
    filters=Filters.chat_type.groups,
    run_async=True,
)

RMBTN_HANDLER = CallbackQueryHandler(rmbutton, pattern=r"rmnotes_", run_async=True)

dispatcher.add_handler(GET_HANDLER)
dispatcher.add_handler(SAVE_HANDLER)
dispatcher.add_handler(LIST_HANDLER)
dispatcher.add_handler(DELETE_HANDLER)
dispatcher.add_handler(HASH_GET_HANDLER)
dispatcher.add_handler(CLEARALLNOTES_HANDLER)
dispatcher.add_handler(RMBTN_HANDLER)
