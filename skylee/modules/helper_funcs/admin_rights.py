from typing import Optional

from telegram import (
          User, 
          Chat, 
          ChatMember, 
          Update, 
          Bot)

def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
	return chat.get_member(user.id).can_promote_members
	
def user_can_ban(chat: Chat, user: User, bot_id: int) -> bool:
	return chat.get_member(user.id).can_restrict_members
	
def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
	return chat.get_member(user.id).can_pin_messages

