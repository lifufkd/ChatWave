from models import Users, Conversations
from repository import (
    check_user_is_existed,
    get_user_conversations_from_db,
    add_conversation_in_db,
    add_conversation_members_in_db,
    add_members_to_conversation_in_db
)
from utilities import UserNotFoundError, ChatAlreadyExists, ConversationTypes, SameUsersIds, ConversationMemberRoles
from schemas import CreateGroup


async def add_chat_conversation(current_user_id: int, companion_id: int):

    def get_conversations_ids(user_obj: Users) -> list[int]:
        temp = list()
        for conversation_obj in user_obj.conversations:
            temp.append(conversation_obj.id)

        return temp

    if current_user_id == companion_id:
        raise SameUsersIds()

    if await check_user_is_existed(current_user_id) is None:
        raise UserNotFoundError()
    if await check_user_is_existed(companion_id) is None:
        raise UserNotFoundError()

    current_user_obj = await get_user_conversations_from_db(current_user_id)
    companion_obj = await get_user_conversations_from_db(companion_id)
    current_user_conversations_ids = get_conversations_ids(current_user_obj)
    companion_conversations_ids = get_conversations_ids(companion_obj)

    if set(current_user_conversations_ids) & set(companion_conversations_ids):
        raise ChatAlreadyExists()

    new_conversation_obj = Conversations(
        creator_id=current_user_id,
        type=ConversationTypes.PRIVATE,
    )
    await add_conversation_in_db(new_conversation_obj)
    await add_conversation_members_in_db(
        users_objects=[current_user_obj, companion_obj],
        conversation_id=new_conversation_obj.id,
        role=ConversationMemberRoles.MEMBER
    )


async def add_group_conversation(current_user_id: int, group_data: CreateGroup):
    if await check_user_is_existed(current_user_id) is None:
        raise UserNotFoundError()

    current_user_obj = await get_user_conversations_from_db(current_user_id)

    new_conversation_obj = Conversations(
        creator_id=current_user_id,
        type=ConversationTypes.GROUP,
        **group_data.model_dump(exclude_none=True)
    )
    await add_conversation_in_db(new_conversation_obj)
    await add_conversation_members_in_db(
        users_objects=[current_user_obj],
        conversation_id=new_conversation_obj.id,
        role=ConversationMemberRoles.CREATOR
    )



