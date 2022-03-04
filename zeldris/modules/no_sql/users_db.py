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

"""Users Database."""

from zeldris import dispatcher
from zeldris.modules.no_sql import get_collection

USERS_DB = get_collection("USERS")
CHATS_DB = get_collection("CHATS")
CHAT_MEMBERS_DB = get_collection("CHAT_MEMBERS")


def ensure_bot_in_db():
    USERS_DB.update_one(
        {"_id": dispatcher.bot.id},
        {"$set": {"username": dispatcher.bot.username}},
        upsert=True,
    )


def update_user(user_id, username, chat_id=None, chat_name=None):
    USERS_DB.update_one({"_id": user_id}, {"$set": {"username": username}}, upsert=True)

    if not (chat_id or chat_name):
        return

    CHATS_DB.update_one(
        {"chat_id": chat_id}, {"$set": {"chat_name": chat_name}}, upsert=True
    )

    member = CHAT_MEMBERS_DB.find_one({"chat_id": chat_id, "user_id": user_id})
    if member is None:
        CHAT_MEMBERS_DB.insert_one({"chat_id": chat_id, "user_id": user_id})


def get_userid_by_name(username) -> dict:
    return list(USERS_DB.find({"username": username}))


def get_name_by_userid(user_id) -> dict:
    return list(USERS_DB.find_one({"_id": user_id}))


def get_chat_members(chat_id) -> list:
    return list(CHAT_MEMBERS_DB.find({"chat_id": chat_id}))


def get_all_chats() -> list:
    return list(CHATS_DB.find())


def get_all_users() -> list:
    return list(USERS_DB.find())


def get_user_num_chats(user_id) -> int:
    return CHAT_MEMBERS_DB.count_documents({"user_id": user_id})


def get_user_com_chats(user_id) -> int:
    return list(CHAT_MEMBERS_DB.find({"user_id": user_id}))


def num_chats() -> int:
    return CHATS_DB.count_documents({})


def num_users() -> int:
    return USERS_DB.count_documents({})


def rem_chat(chat_id) -> None:
    CHATS_DB.delete_one({"chat_id": chat_id})


def migrate_chat(old_chat_id, new_chat_id) -> None:
    CHATS_DB.update_one({"chat_id": old_chat_id}, {"$set": {"chat_id": new_chat_id}})

    chat_members = CHAT_MEMBERS_DB.find({"chat_id": old_chat_id})
    for member in chat_members:
        CHAT_MEMBERS_DB.update_one(
            {"chat_id": member["chat_id"]}, {"$set": {"chat_id": new_chat_id}}
        )


ensure_bot_in_db()
