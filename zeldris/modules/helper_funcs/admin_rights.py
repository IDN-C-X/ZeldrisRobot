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


from telegram import User, Chat


def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_promote_members


def user_can_ban(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_restrict_members


def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_pin_messages


def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_change_info


def user_can_delete(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_delete_messages
