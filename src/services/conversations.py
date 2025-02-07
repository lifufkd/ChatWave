from pathlib import Path

from validators import (
    validate_user_in_conversation,
    validate_user_can_manage_conversation,
    validate_user_in_group,
    validate_user_in_groups,
    validate_users_in_same_chat,
    get_conversations_ids_from_user_obj,
    conversation_is_group,
    validate_user_in_chat,
    verify_user_is_existed
)
from repository import (
    select_conversation,
    insert_members_to_conversation,
    select_conversation_by_id,
    update_conversation,
    select_conversations,
    select_user,
    delete_conversation_avatar,
    select_conversation_member_role,
    delete_conversation_members,
    delete_conversation,
    delete_sender_messages,
    select_conversation_members_quantity,
    select_conversation_members,
    select_conversation_admin_members,
    update_conversation_member,
    delete_conversation_messages
)
from storage import FileManager
from utilities import (
    UserNotFoundError,
    ConversationTypes,
    SameUsersIds,
    ConversationMemberRoles,
    FileNotFound,
    UserAlreadyInConversation,
    MessagesTypes,
    sqlalchemy_to_pydantic,
    MediaPatches
)
from schemas import (
    CreateGroup,
    EditConversation,
    EditConversationDB,
    DeleteGroupMembers,
    CreateEmptyConversation,
    GetConversations,
    Avatar,
    CreateGroupDB
)


async def create_private_conversation(user_id: int, recipient_id: int) -> GetConversations:
    await verify_user_is_existed(user_id=recipient_id)
    await validate_users_in_same_chat(user_id=user_id, recipient_id=recipient_id)

    new_conversation_obj = CreateEmptyConversation(
        creator_id=user_id,
        type=ConversationTypes.PRIVATE,
    )
    new_conversation_id = await select_conversation(new_conversation_obj)
    raw_new_conversation = await select_conversation_by_id(conversation_id=new_conversation_id)
    new_conversation_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=raw_new_conversation,
        pydantic_model=GetConversations
    )
    await insert_members_to_conversation(
        users_ids=[user_id, recipient_id],
        conversation_id=new_conversation_id,
        role=ConversationMemberRoles.MEMBER
    )

    return new_conversation_obj


async def create_group_conversation(user_id: int, group_data: CreateGroup) -> GetConversations:
    new_conversation_obj = CreateGroupDB(
        creator_id=user_id,
        type=ConversationTypes.GROUP,
        **group_data.model_dump()
    )

    new_conversation_id = await select_conversation(new_conversation_obj)
    raw_new_conversation = await select_conversation_by_id(conversation_id=new_conversation_id)
    new_conversation_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=raw_new_conversation,
        pydantic_model=GetConversations
    )
    await insert_members_to_conversation(
        users_ids=[user_id],
        conversation_id=new_conversation_id,
        role=ConversationMemberRoles.CREATOR
    )

    return new_conversation_obj


async def edit_group_details(user_id: int, group_id: int, group_data: EditConversation):
    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    edit_conversation_obj = EditConversationDB(**group_data.model_dump())
    await update_conversation(
        conversation_id=group_id,
        conversation_obj=edit_conversation_obj
    )


async def add_group_members(user_id: int, group_id: int, users_ids: list[int]) -> None:
    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    members_ids = list()
    for member_id in users_ids:
        member_obj = await select_user(user_id=member_id)
        if member_obj is None:
            raise UserNotFoundError(user_id=member_id)

        member_conversations_ids = await get_conversations_ids_from_user_obj(member_obj)
        if group_id in member_conversations_ids:
            raise UserAlreadyInConversation(
                user_id=member_id,
                conversation_id=group_id
            )

        members_ids.append(member_obj.id)

    await insert_members_to_conversation(
        users_ids=members_ids,
        conversation_id=group_id,
        role=ConversationMemberRoles.MEMBER
    )


async def upload_group_avatar(user_id: int, group_id: int, avatar_data: Avatar) -> None:

    async def save_avatar_to_file():
        await FileManager().validate_file(
            file_content=avatar_data.file,
            file_type=avatar_data.content_type,
            file_type_filter=MessagesTypes.IMAGE
        )
        avatar_save_path = MediaPatches.GROUPS_AVATARS_FOLDER.value / avatar_name
        await FileManager().write_file(file_path=avatar_save_path, file_data=avatar_data.file)

    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    avatar_name = f"{group_id}.{avatar_data.file_name.split('.')[-1]}"
    await save_avatar_to_file()
    await update_conversation(
        conversation_id=group_id,
        conversation_obj=EditConversationDB(
            avatar_name=avatar_name,
            avatar_type=avatar_data.content_type
        )
    )


async def fetch_group_avatar_metadata(user_id: int, group_id: int) -> dict[str, any]:
    await validate_user_in_group(user_id=user_id, group_id=group_id)

    group_obj = await select_conversation_by_id(conversation_id=group_id)
    filepath = MediaPatches.GROUPS_AVATARS_FOLDER.value / f"{group_obj.avatar_name}"
    if not (await FileManager().file_exists(file_path=filepath)):
        raise FileNotFound()

    return {
        "file_path": filepath,
        "file_type": group_obj.avatar_type
    }


async def fetch_group_avatars_paths(user_id: int, conversations_ids: list[int]) -> list[Path]:
    await validate_user_in_groups(user_id=user_id, groups_ids=conversations_ids)

    avatars_paths = list()
    groups_objects = await select_conversations(conversations_ids=conversations_ids)
    for group_obj in groups_objects:
        if group_obj.avatar_name is None:
            continue

        avatars_paths.append(MediaPatches.GROUPS_AVATARS_FOLDER.value / group_obj.avatar_name)

    if not avatars_paths:
        raise FileNotFound()

    return avatars_paths


async def remove_group_avatar(user_id: int, group_id: int, avatar_path: Path) -> None:
    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    await FileManager().delete_file(file_path=avatar_path)
    await delete_conversation_avatar(conversation_id=group_id)


async def remove_group_members(user_id: int, group_id: int, members_data: list[DeleteGroupMembers]) -> None:
    members_ids_to_delete_messages = list()
    members_ids = [member.user_id for member in members_data]

    if user_id in members_ids:
        raise SameUsersIds()
    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    for member_obj in members_data:
        await verify_user_is_existed(user_id=member_obj.user_id)
        await validate_user_in_conversation(user_id=member_obj.user_id, conversation_id=group_id)
        if not member_obj.delete_messages:
            continue

        members_ids_to_delete_messages.append(member_obj.user_id)

    await delete_conversation_members(conversation_id=group_id, members_ids=members_ids)
    await delete_sender_messages(conversation_id=group_id, members_ids=members_ids_to_delete_messages)


async def delete_conversation_by_id(user_id: int, conversation_id: int) -> None:
    await validate_user_can_manage_conversation(user_id=user_id, conversation_id=conversation_id)
    await delete_conversation(conversation_id=conversation_id)


async def leave_group(user_id: int, group_id: int, delete_messages: bool = False) -> None:

    async def get_new_admin_user_id() -> int:
        group_users_ordered_by_join_time = await select_conversation_members(conversation_id=group_id)
        for member_obj in group_users_ordered_by_join_time:
            if user_id == member_obj.user_id:
                continue
            return member_obj.user_id

    await validate_user_in_group(user_id=user_id, group_id=group_id)

    group_members_quantity = await select_conversation_members_quantity(conversation_id=group_id)
    if group_members_quantity == 1:
        await delete_conversation(conversation_id=group_id)
    else:
        user_group_role = await select_conversation_member_role(user_id=user_id, conversation_id=group_id)
        if user_group_role != ConversationMemberRoles.MEMBER:

            admin_users_quantity = len((await select_conversation_admin_members(conversation_id=group_id)))
            if admin_users_quantity == 1:
                new_admin_user_id = await get_new_admin_user_id()
                await update_conversation_member(
                    conversation_id=group_id,
                    member_id=new_admin_user_id,
                    role=ConversationMemberRoles.ADMIN
                )

        if delete_messages:
            await delete_sender_messages(conversation_id=group_id, members_ids=[user_id])

        await delete_conversation_members(conversation_id=group_id, members_ids=[user_id])


async def delete_all_messages(user_id: int, conversation_id: int):
    await validate_user_in_chat(user_id=user_id, chat_id=conversation_id)
    await delete_conversation_messages(conversation_id=conversation_id)
