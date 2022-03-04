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

"""Global Bans Database"""

from zeldris.modules.no_sql import get_collection

GBAN_USER = get_collection("GBANS")
GBAN_SETTINGS = get_collection("GBAN_SETTINGS")
GBANNED_LIST = set()
GBANSTAT_LIST = set()


def gban_user(user_id, name, reason=None) -> None:
    GBAN_USER.insert_one(
        {
            "_id": user_id,
            "name": name,
            "reason": reason,
        }
    )
    __load_gbanned_userid_list()


def update_gban_reason(user_id, name, reason) -> str:
    data = GBAN_USER.find_one_and_update(
        {"_id": user_id}, {"$set": {"name": name, "reason": reason}}, upsert=False
    )
    return data["reason"]


def ungban_user(user_id) -> None:
    GBAN_USER.delete_one({"_id": user_id})
    __load_gbanned_userid_list()


def is_user_gbanned(user_id):
    return user_id in GBANNED_LIST


def get_gbanned_user(user_id):
    return GBAN_USER.find_one({"_id": user_id})


def get_gban_list() -> dict:
    return list(GBAN_USER.find())


def enable_gbans(chat_id) -> None:
    __gban_setting(chat_id, True)
    if str(chat_id) in GBANSTAT_LIST:
        GBANSTAT_LIST.remove(str(chat_id))


def disable_gbans(chat_id) -> None:
    __gban_setting(chat_id, False)
    GBANSTAT_LIST.add(str(chat_id))


def __gban_setting(chat_id, setting: bool = True) -> None:
    if GBAN_SETTINGS.find_one({"_id": chat_id}):
        GBAN_SETTINGS.update_one({"_id": chat_id}, {"$set": {"setting": setting}})
    else:
        GBAN_SETTINGS.insert_one({"_id": chat_id, "setting": setting})


def does_chat_gban(chat_id) -> bool:
    return str(chat_id) not in GBANSTAT_LIST


def num_gbanned_users() -> int:
    return len(GBANNED_LIST)


def __load_gbanned_userid_list() -> None:
    global GBANNED_LIST
    GBANNED_LIST = {i["_id"] for i in GBAN_USER.find()}


def __load_gban_stat_list() -> None:
    global GBANSTAT_LIST
    GBANSTAT_LIST = {str(i["_id"]) for i in GBAN_SETTINGS.find() if not i["setting"]}


def migrate_chat(old_chat_id, new_chat_id) -> None:
    old = GBAN_SETTINGS.find_one_and_delete({"_id": old_chat_id})
    setting = old["setting"] if old else True
    GBAN_SETTINGS.update_one(
        {"_id": new_chat_id},
        {"$set": {"setting": setting}},
        upsert=True,
    )


# Create in memory userid to avoid disk access
__load_gbanned_userid_list()
__load_gban_stat_list()
