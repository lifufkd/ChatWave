from repository import check_is_conversation_existed, get_user_from_db
from models import Users
from utilities import ConversationNotFoundError, AccessDeniedError


async def get_user_conversation_ids(user_obj: Users) -> list[int]:
    temp = list()
    for conversation_obj in user_obj.conversations:
        temp.append(conversation_obj.id)

    return temp


async def conversation_is_existed(conversation_id: int) -> None:
    if not (await check_is_conversation_existed(conversation_id=conversation_id)):
        raise ConversationNotFoundError()


async def validate_user_in_conversation(user_id: int, conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)
    current_user_obj = await get_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)
    if conversation_id not in current_user_conversations_ids:
        raise AccessDeniedError()


async def validate_user_in_conversations(user_id: int, conversations_ids: list[int]) -> None:
    current_user_obj = await get_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)

    for conversation_id in conversations_ids:
        await conversation_is_existed(conversation_id=conversation_id)
    if not set(current_user_conversations_ids).intersection(set(conversations_ids)):
        raise AccessDeniedError()