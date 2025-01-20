from io import BytesIO
from pathlib import Path
from fastapi import UploadFile

from models import Users, Conversations
from repository import (
    check_user_is_existed,
    add_conversation_in_db,
    add_conversation_members_in_db,
    get_conversation_from_db,
    update_conversation_in_db,
    get_conversations_from_db,
    get_user_from_db,
    check_is_conversation_existed,
    get_conversation_type,
    delete_conversation_avatar_from_db,
    get_conversation_member_role_from_db
)
from utilities import (
    UserNotFoundError,
    ChatAlreadyExists,
    ConversationTypes,
    SameUsersIds,
    IsNotAGroupError,
    ConversationMemberRoles,
    ConversationNotFoundError,
    AccessDeniedError,
    FileManager,
    generic_settings,
    FileNotFound,
    UserAlreadyInConversation,
    MessagesTypes
)
from schemas import CreateGroup, EditConversation, EditConversationExtended, GroupsAvatars, AddMembersToConversation


async def get_conversations_ids(user_obj: Users) -> list[int]:
    temp = list()
    for conversation_obj in user_obj.conversations:
        temp.append(conversation_obj.id)

    return temp


async def validate_group(current_user_id: int, group_id: int):
    if not (await check_is_conversation_existed(conversation_id=group_id)):
        raise ConversationNotFoundError()
    if (await get_conversation_type(conversation_id=group_id)) != ConversationTypes.GROUP:
        raise IsNotAGroupError()

    current_user_obj = await get_user_from_db(current_user_id)
    current_user_conversations_ids = await get_conversations_ids(current_user_obj)
    if group_id not in current_user_conversations_ids:
        raise AccessDeniedError()


async def add_chat_conversation(current_user_id: int, companion_id: int):

    if current_user_id == companion_id:
        raise SameUsersIds()

    if not (await check_user_is_existed(user_id=current_user_id)):
        raise UserNotFoundError()

    current_user_obj = await get_user_from_db(current_user_id)
    companion_obj = await get_user_from_db(companion_id)
    current_user_conversations_ids = await get_conversations_ids(current_user_obj)
    companion_conversations_ids = await get_conversations_ids(companion_obj)

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

    current_user_obj = await get_user_from_db(current_user_id)

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


async def update_conversation(current_user_id: int, group_id: int, group_obj: EditConversation):
    await validate_group(current_user_id, group_id)
    user_role_in_group = await get_conversation_member_role_from_db(user_id=current_user_id, conversation_id=group_id)
    if (await get_conversation_member_role_from_db(user_id=current_user_id,
                                                   conversation_id=group_id)) == ConversationMemberRoles.MEMBER:
        raise AccessDeniedError()

    edit_conversation_extended_obj = EditConversationExtended(**group_obj.model_dump())
    await update_conversation_in_db(
        conversation_id=group_id,
        conversation_obj=edit_conversation_extended_obj
    )


async def add_members_to_conversation(current_user_id: int, request_data: AddMembersToConversation):
    await validate_group(current_user_id, request_data.group_id)
    if (await get_conversation_member_role_from_db(user_id=current_user_id, conversation_id=request_data.group_id)) == ConversationMemberRoles.MEMBER:
        raise AccessDeniedError()

    users_objs = list()
    for user_id in request_data.users_ids:
        user_obj = await get_user_from_db(user_id=user_id)
        if user_obj is None:
            raise UserNotFoundError(detail=f"User with id {user_id} not found")

        user_conversations_ids = await get_conversations_ids(user_obj)
        if request_data.group_id in user_conversations_ids:
            raise UserAlreadyInConversation(detail=f"User with id {user_id} already in group")

        users_objs.append(user_obj)

    await add_conversation_members_in_db(
        users_objects=users_objs,
        conversation_id=request_data.group_id,
        role=ConversationMemberRoles.MEMBER
    )


async def update_group_avatar(current_user_id: int, group_id: int, avatar: UploadFile) -> None:

    async def save_avatar_to_file():
        FileManager().validate_file(
            file_content=await avatar.read(),
            file_type=avatar.content_type,
            file_type_filter=MessagesTypes.IMAGE
        )
        avatar_save_path = generic_settings.MEDIA_FOLDER / "groups" / "avatars" / avatar_name
        FileManager.write_file(path=avatar_save_path, content=await avatar.read())

    await validate_group(current_user_id, group_id)
    if (await get_conversation_member_role_from_db(user_id=current_user_id,
                                                   conversation_id=group_id)) == ConversationMemberRoles.MEMBER:
        raise AccessDeniedError()

    avatar_name = f"{group_id}.{avatar.filename.split('.')[-1]}"
    await save_avatar_to_file()

    await update_conversation_in_db(
        conversation_id=group_id,
        conversation_obj=EditConversationExtended(
            avatar_name=avatar_name,
            avatar_type=avatar.content_type
        )
    )


async def get_group_avatar_path(current_user_id: int, group_id: int) -> Path:
    await validate_group(current_user_id, group_id)

    group_obj = await get_conversation_from_db(conversation_id=group_id)
    filepath = generic_settings.MEDIA_FOLDER / "groups" / "avatars" / f"{group_obj.avatar_name}"
    if not FileManager.file_exists(path=filepath):
        raise FileNotFound()

    return filepath


async def get_groups_avatars_paths(current_user_id: int, request_obj: GroupsAvatars) -> list[Path]:
    for group_id in request_obj.conversations_ids:
        if not (await check_is_conversation_existed(conversation_id=group_id)):
            raise ConversationNotFoundError()
        if (await get_conversation_type(conversation_id=group_id)) != ConversationTypes.GROUP:
            raise IsNotAGroupError()

    current_user_obj = await get_user_from_db(current_user_id)
    current_user_conversations_ids = await get_conversations_ids(current_user_obj)

    if not set(current_user_conversations_ids).intersection(set(request_obj.conversations_ids)):
        raise AccessDeniedError()

    avatars_paths = list()
    avatar_base_path = generic_settings.MEDIA_FOLDER / "groups" / "avatars"
    groups_objects = await get_conversations_from_db(conversations_ids=request_obj.conversations_ids)
    for group_obj in groups_objects:
        if group_obj.avatar_name is None:
            continue

        avatars_paths.append(avatar_base_path / group_obj.avatar_name)

    if not avatars_paths:
        raise FileNotFound()

    return avatars_paths


async def delete_group_avatar(current_user_id: int, group_id: int,  avatar_path: Path) -> None:
    await validate_group(current_user_id, group_id)
    if (await get_conversation_member_role_from_db(user_id=current_user_id,
                                                   conversation_id=group_id)) == ConversationMemberRoles.MEMBER:
        raise AccessDeniedError()

    FileManager.delete_file(path=avatar_path)
    await delete_conversation_avatar_from_db(conversation_id=group_id)



