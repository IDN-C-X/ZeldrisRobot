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
import io
import os

# Common imports for eval
import textwrap
import traceback
from contextlib import redirect_stdout, suppress
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from zeldris import LOGGER, TOKEN, dispatcher
from zeldris.modules.helper_funcs.chat_status import dev_plus

namespaces = {}


def namespace_of(chat, update, context):
    if chat not in namespaces:
        namespaces[chat] = {
            "__builtins__": globals()["__builtins__"],
            "update": update,
            "context": context,
        }

    return namespaces[chat]


def log_input(update):
    user = update.effective_user.id
    chat = update.effective_chat.id
    LOGGER.info(f"IN: {update.effective_message.text} (user={user}, chat={chat})")


def send(msg, update, bot):
    if len(str(msg)) > 2000:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "output.txt"
            bot.send_document(chat_id=update.effective_chat.id, document=out_file)
    else:
        LOGGER.info(f"OUT: '{msg}'")
        bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"`{msg}`",
            parse_mode=ParseMode.MARKDOWN,
        )


@dev_plus
def evaluate(update: Update, context: CallbackContext):
    bot = context.bot
    send(do(eval, update, context), update, bot)


@dev_plus
def execute(update: Update, context: CallbackContext):
    bot = context.bot
    send(do(exec, update, context), update, bot)


def cleanup_code(code):
    if code.startswith("```") and code.endswith("```"):
        return "\n".join(code.split("\n")[1:-1])
    return code.strip("` \n")


def do(func, update, context):  # skipcq
    log_input(update)
    content = update.message.text.split(" ", 1)[-1]
    body = cleanup_code(content)
    env = namespace_of(update.message.chat_id, update, context)

    os.chdir(os.getcwd())
    with open(
        os.path.join(os.getcwd(), "zeldris/modules/helper_funcs/temp.txt"),
        "w",
    ) as temp:
        temp.write(body)

    stdout = io.StringIO()

    to_compile = f'def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:  # skipcq PYL-W0703
        return f"{e.__class__.__name__}: {e}"

    func = env["func"]

    try:
        with redirect_stdout(stdout):
            func_return = func()
    except Exception:  # skipcq PYL-W0703
        value = stdout.getvalue()
        return f"{value}{traceback.format_exc()}"

    value = stdout.getvalue()
    result = None
    if func_return is None:
        if value:
            result = f"{value}"
        else:
            with suppress(Exception):
                result = f"{repr(eval(body, env))}"
    else:
        result = f"{value}{func_return}"

    if result:
        # don't send results if it has bot token inside.
        if TOKEN in result:
            result = "Results includes bot TOKEN, aborting..."
        return result


@dev_plus
def clear(update: Update, context: CallbackContext):
    bot = context.bot
    log_input(update)
    global namespaces
    if update.message.chat_id in namespaces:
        del namespaces[update.message.chat_id]
    send("Cleared locals.", bot, update)


EVAL_HANDLER = CommandHandler(
    ("e", "ev", "eva", "eval"),
    evaluate,
    run_async=True,
)
EXEC_HANDLER = CommandHandler(
    ("x", "ex", "exe", "exec", "py"),
    execute,
    run_async=True,
)
CLEAR_HANDLER = CommandHandler("clearlocals", clear, run_async=True)

dispatcher.add_handler(EVAL_HANDLER)
dispatcher.add_handler(EXEC_HANDLER)
dispatcher.add_handler(CLEAR_HANDLER)

__mod_name__ = "Eval Module"
