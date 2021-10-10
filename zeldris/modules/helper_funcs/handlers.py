import telegram.ext as tg
from telegram import Update

from pyrate_limiter import (
    BucketFullException,
    Duration,
    RequestRate,
    Limiter,
    MemoryListBucket,
)

from zeldris import LOGGER, DEV_USERS, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS

try:
    from zeldris import CUSTOM_CMD
except BaseException:
    CUSTOM_CMD = False

if CUSTOM_CMD:
    CMD_STARTERS = CUSTOM_CMD
    LOGGER.debug("Bot custom command handler = \"%s\"", CMD_STARTERS)
else:
    CMD_STARTERS = ["/", "!"]
                    
                    
class AntiSpam:
    def __init__(self):
        self.whitelist = (
            (DEV_USERS or [])
            + (SUDO_USERS or [])
            + (WHITELIST_USERS or [])
            + (SUPPORT_USERS or [])
        )
        # Values are HIGHLY experimental, its recommended you pay attention to our commits as we will be adjusting the values over time with what suits best.
        Duration.CUSTOM = 15  # Custom duration, 15 seconds
        self.sec_limit = RequestRate(6, Duration.CUSTOM)  # 6 / Per 15 Seconds
        self.min_limit = RequestRate(20, Duration.MINUTE)  # 20 / Per minute
        self.hour_limit = RequestRate(100, Duration.HOUR)  # 100 / Per hour
        self.daily_limit = RequestRate(1000, Duration.DAY)  # 1000 / Per day
        self.limiter = Limiter(
            self.sec_limit,
            self.min_limit,
            self.hour_limit,
            self.daily_limit,
            bucket_class=MemoryListBucket,
        )

    def check_user(self, user):
        """
        Return True if user is to be ignored else False
        """
        if user in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user)
            return False
        except BucketFullException:
            return True


SpamChecker = AntiSpam()
MessageHandlerChecker = AntiSpam()


class CustomCommandHandler(tg.CommandHandler):
    def __init__(self, command, callback, **kwargs):
        if "admin_ok" in kwargs:
            del kwargs["admin_ok"]
        super().__init__(command, callback, **kwargs)

    def check_update(self, update):
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]
                if len(fst_word) > 1 and any(
                    fst_word.startswith(start) for start in CMD_STARTERS
                ):
                    args = message.text.split()[1:]
                    command = fst_word[1:].split("@")
                    command.append(
                        message.bot.username
                    )  # in case the command was sent without a username

                    if not (
                        command[0].lower() in self.command
                        and command[1].lower() == message.bot.username.lower()
                    ):
                        return None

                    if SpamChecker.check_user(user_id):
                        return None

                    filter_result = self.filters(update)
                    if filter_result:
                        return args, filter_result
                    else:
                        return False
