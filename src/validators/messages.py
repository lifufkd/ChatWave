from validators.conversations import conversation_is_existed
from repository import (
    is_message_exists,
    select_message,
    select_messages,
    select_conversation_member_role
)
from utilities import (
    MessageNotFound,
    AccessDeniedError,
    ConversationTypes,
    ConversationMemberRoles,
    UserNotInConversation
)
from validators import validate_user_in_conversation, validate_user_in_conversations


async def get_conversations_ids_from_messages(messages_objs: list) -> list[int]:
    temp = list()
    for message_obj in messages_objs:
        temp.append(message_obj.conversation_id)

    return temp


async def message_is_existed(message_id: int) -> None:
    if not (await is_message_exists(message_id=message_id)):
        raise MessageNotFound(message_id=message_id)


async def messages_is_existed(messages_ids: list[int]) -> None:
    for message_id in messages_ids:
        await message_is_existed(message_id=message_id)


async def validate_user_is_message_owner(user_id: int, message_id: int) -> None:
    await message_is_existed(message_id=message_id)

    message_obj = await select_message(message_id=message_id)
    await validate_user_in_conversation(user_id=user_id, conversation_id=message_obj.conversation_id)

    if message_obj.sender_id != user_id:
        raise AccessDeniedError()


async def validate_user_have_access_to_message(user_id: int, message_id: int) -> None:
    await message_is_existed(message_id=message_id)

    message_obj = await select_message(message_id=message_id)
    await validate_user_in_conversation(user_id=user_id, conversation_id=message_obj.conversation_id)


async def validate_user_have_access_to_messages(user_id: int, messages_ids: list[int]) -> None:
    await messages_is_existed(messages_ids=messages_ids)

    messages_objs = await select_messages(messages_ids=messages_ids)
    conversations_ids = await get_conversations_ids_from_messages(messages_objs=messages_objs)
    await validate_user_in_conversations(user_id=user_id, conversations_ids=conversations_ids)


async def validate_user_can_manage_messages(user_id: int, messages_ids: list[int]) -> None:
    await messages_is_existed(messages_ids=messages_ids)

    messages_objs = await select_messages(messages_ids=messages_ids)

    for message_obj in messages_objs:
        await conversation_is_existed(conversation_id=message_obj.conversation_id)

        conversation_type = message_obj.conversation.type
        user_role = await select_conversation_member_role(
            user_id=user_id,
            conversation_id=message_obj.conversation_id
        )

        if user_role is None:
            raise UserNotInConversation(user_id=user_id, conversation_id=message_obj.conversation_id)

        if conversation_type == ConversationTypes.GROUP:
            if user_role == ConversationMemberRoles.MEMBER:
                raise AccessDeniedError()
