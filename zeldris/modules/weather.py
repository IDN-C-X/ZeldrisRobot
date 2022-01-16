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


import json
import time

import requests
from pytz import country_names as cname
from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from zeldris import dispatcher, API_WEATHER as APPID
from zeldris.modules.disable import DisableAbleCommandHandler
from zeldris.modules.helper_funcs.alternate import typing_action


@typing_action
def weather(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        reply = "Write a location to check the weather."
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
            if err.message in (
                "Message to delete not found",
                "Message can't be deleted",
            ):
                return

        return

    city = " ".join(args)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={APPID}"
    request = requests.get(url)
    result = json.loads(request.text)
    if request.status_code != 200:
        reply = "Location not valid."
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
            if err.message in (
                "Message to delete not found",
                "Message can't be deleted",
            ):
                return
        return

    try:
        cityname = result["name"]
        curtemp = result["main"]["temp"]
        feels_like = result["main"]["feels_like"]
        humidity = result["main"]["humidity"]
        wind = result["wind"]["speed"]
        weath = result["weather"][0]
        icon = weath["id"]
        condmain = weath["main"]
        conddet = weath["description"]
        country_name = cname[f"{result['sys']['country']}"]
    except KeyError:
        update.effective_message.reply_text("Invalid Location!")
        return

    if icon <= 232:  # Rain storm
        icon = "⛈"
    elif icon <= 321:  # Drizzle
        icon = "🌧"
    elif icon <= 504:  # Light rain
        icon = "🌦"
    elif icon <= 531:  # Cloudy rain
        icon = "⛈"
    elif icon <= 622:  # Snow
        icon = "❄️"
    elif icon <= 781:  # Atmosphere
        icon = "🌪"
    elif icon <= 800:  # Bright
        icon = "☀️"
    elif icon <= 801:  # A little cloudy
        icon = "⛅️"
    elif icon <= 804:  # Cloudy
        icon = "☁️"
    kmph = str(wind * 3.6).split(".")

    def celsius(c):
        k = 273.15
        c = k if (c > (k - 1)) and (c < k) else c
        return str(round((c - k)))

    def fahr(c):
        c1 = 9 / 5
        c2 = 459.67
        t_f = c * c1 - c2
        if 0 > t_f > -1:
            t_f = 0
        return str(round(t_f))

    reply = (
        f"*Current weather for {cityname}, {country_name} is*:\n\n"
        f"*Temperature:* `{celsius(curtemp)}°C ({fahr(curtemp)}ºF), "
        f"feels like {celsius(feels_like)}°C ({fahr(feels_like)}ºF) \n"
        f"`*Condition:* `{condmain}, {conddet}` {icon}\n"
        f"*Humidity:* `{humidity}%`\n*Wind:* `{kmph[0]} km/h`\n "
    )
    del_msg = update.effective_message.reply_text(
        "{}".format(reply), parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
    )
    time.sleep(30)
    try:
        del_msg.delete()
        update.effective_message.delete()
    except BadRequest as err:
        if err.message in ("Message to delete not found", "Message can't be deleted"):
            return


__help__ = r"""
Weather module:

× /weather <city>: Gets weather information of particular place!

\* To prevent spams weather command and the output will be deleted after 30 seconds
"""

__mod_name__ = "Weather"

WEATHER_HANDLER = DisableAbleCommandHandler("weather", weather, pass_args=True)

dispatcher.add_handler(WEATHER_HANDLER)
