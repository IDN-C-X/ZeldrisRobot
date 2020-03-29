import random, re
import wikipedia
from typing import Optional, List
from random import randint
from telegram import Message, Update, Bot, User
from telegram import MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters, CommandHandler, MessageHandler, run_async
from telegram import TelegramError, Chat, Message
from telegram.error import BadRequest
from skylee.modules.helper_funcs.filters import CustomFilters
from skylee import dispatcher
from skylee.modules.disable import DisableAbleCommandHandler

#Abuse strings credits @NotAMemeBot
ABUSE_STRINGS = (
    "Fuck off",
    "Stfu go fuck yourself",
    "you noob",
    "Relax your Rear,ders nothing to fear,The Rape train is finally here",
    "Stfu bc",
    "Stfu and Gtfo U nub",
    "CUnt",
    "Gay is here",
    "Owww ... Such a stupid idiot.",
    "Don't drink and type.",
    "I think you should go home or better a mental asylum.",
    "Command not found. Just like your brain.",
    "Do you realize you are making a fool of yourself? Apparently not.",
    "You can type better than that.",
    "Bot rule 544 section 9 prevents me from replying to stupid humans like you.",
    "Sorry, we do not sell brains.",
    "Believe me you are not normal.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "Zombies eat brains... you're safe.",
    "You didn't evolve from apes, they evolved from you.",
    "Come back and talk to me when your I.Q. exceeds your age.",
    "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.",
    "What language are you speaking? Cause it sounds like bullshit.",
    "Stupidity is not a crime so you are free to go.",
    "You are proof that evolution CAN go in reverse.",
    "I would ask you how old you are but I know you can't count that high.",
    "As an outsider, what do you think of the human race?",
    "Brains aren't everything. In your case they're nothing.",
    "Ordinarily people live and learn. You just live.",
    "I don't know what makes you so stupid, but it really works.",
    "Keep talking, someday you'll say something intelligent! (I doubt it though)",
    "Shock me, say something intelligent.",
    "Your IQ's lower than your shoe size.",
    "Alas! Your neurotransmitters are no more working.",
    "Are you crazy you fool.",
    "Everyone has the right to be stupid but you are abusing the privilege.",
    "I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.",
    "You should try tasting cyanide.",
    "Your enzymes are meant to digest rat poison.",
    "You should try sleeping forever.",
    "Pick up a gun and shoot yourself.",
    "You could make a world record by jumping from a plane without parachute.",
    "Stop talking BS and jump in front of a running bullet train.",
    "Try bathing with Hydrochloric Acid instead of water.",
    "Try this: if you hold your breath underwater for an hour, you can then hold it forever.",
    "Go Green! Stop inhaling Oxygen.",
    "God was searching for you. You should leave to meet him.",
    "give your 100%. Now, go donate blood.",
    "Try jumping from a hundred story building but you can do it only once.",
    "You should donate your brain seeing that you never used it.",
    "Volunteer for target in an firing range.",
    "Head shots are fun. Get yourself one.",
    "You should try swimming with great white sharks.",
    "You should paint yourself red and run in a bull marathon.",
    "You can stay underwater for the rest of your life without coming back up.",
    "How about you stop breathing for like 1 day? That'll be great.",
    "Try provoking a tiger while you both are in a cage.",
    "Have you tried shooting yourself as high as 100m using a canon.",
    "You should try holding TNT in your mouth and igniting it.",
    "Try playing catch and throw with RDX its fun.",
    "I heard phogine is poisonous but i guess you wont mind inhaling it for fun.",
    "Launch yourself into outer space while forgetting oxygen on Earth.",
    "You should try playing snake and ladders, with real snakes and no ladders.",
    "Dance naked on a couple of HT wires.",
    "Active Volcano is the best swimming pool for you.",
    "You should try hot bath in a volcano.",
    "Try to spend one day in a coffin and it will be yours forever.",
    "Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.",
    "You can be the first person to step on sun. Have a try.",
)

@run_async
def abuse(update, context):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text(random.choice(ABUSE_STRINGS))

@run_async
def shrug(update, context):
    # reply to correct message
    reply_text = update.effective_message.reply_to_message.reply_text if update.effective_message.reply_to_message else update.effective_message.reply_text
    reply_text("¯\_(ツ)_/¯")

@run_async
def decide(update, context):
        r = randint(1, 100)
        if r <= 65:
            update.message.reply_text("Yes.")
        elif r <= 90:
            update.message.reply_text("NoU.")
        else:
            update.message.reply_text("Maybe.")

@run_async
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
def wiki(update, context):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔧 More Info...", url=wikipedia.page(kueri).url)]])
            context.bot.editMessageText(chat_id=update.effective_chat.id, message_id=pertama.message_id, text=wikipedia.summary(kueri, sentences=10), reply_markup=keyboard)
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et :
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}")

__help__ = """
Some random extra commands for fun!

 - /shrug : get shrug 🤷
 - /decide : Randomly answers yes/no/maybe
 - /abuse : Abuses the retard!
 - /wiki  : Search the wikipedia articles.
"""

__mod_name__ = "Extras"

SHRUG_HANDLER = DisableAbleCommandHandler("shrug", shrug)
DECIDE_HANDLER = DisableAbleCommandHandler("decide", decide)
SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True, filters=CustomFilters.sudo_filter)
ABUSE_HANDLER = DisableAbleCommandHandler("abuse", abuse)

WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)


dispatcher.add_handler(SHRUG_HANDLER)
dispatcher.add_handler(DECIDE_HANDLER)
dispatcher.add_handler(ABUSE_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
