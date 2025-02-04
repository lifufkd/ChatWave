from repository import is_unread_messages_exists
from schemas import UnreadMessageExistedDTO
from utilities import UnreadMessageAlreadyExists


async def validate_unread_message_doesnt_exist(filter_conditions: UnreadMessageExistedDTO):
    if await is_unread_messages_exists(filter_conditions=filter_conditions):
        raise UnreadMessageAlreadyExists(user_id=filter_conditions.user_id)
