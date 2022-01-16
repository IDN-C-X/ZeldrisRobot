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


from zeldris import REDIS


# AFK
def is_user_afk(userid):
    rget = REDIS.get(f"is_afk_{userid}")
    return bool(rget)


def start_afk(userid, reason):
    REDIS.set(f"is_afk_{userid}", reason)


def afk_reason(userid):
    return strb(REDIS.get(f"is_afk_{userid}"))


def end_afk(userid):
    REDIS.delete(f"is_afk_{userid}")
    return True


# Helpers
def strb(redis_string):
    return str(redis_string)
