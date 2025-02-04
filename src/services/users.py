from pathlib import Path
from dependencies import redis_client
from repository import (
    update_user_in_db,
    search_users_in_db,
    get_users_last_online_from_db,
    delete_user_avatar_in_db,
    fetch_user_from_db,
    fetch_users_from_db,
    delete_conversation_in_db,
    delete_user_from_db,
    get_conversation_messages_id
)
from validators import verify_user_is_existed, verify_users_is_existed
from schemas import (
    PrivateUser,
    UpdateUser,
    PublicUser,
    UpdateUserDB,
    UserOnline,
    Avatar,
    GetConversations,
    GetConversationsDB,
    GetUnreadMessages
)
from .messages import remove_media_messages, mark_message_delivered
from .conversations import leave_group
from storage import FileManager
from utilities import (
    sqlalchemy_to_pydantic,
    many_sqlalchemy_to_pydantic,
    Hash,
    FileNotFound,
    MessagesTypes,
    ConversationTypes,
    MediaPatches
)


async def fetch_private_user(user_id: int) -> PrivateUser:
    user_raw = await fetch_user_from_db(user_id=user_id)
    user_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=user_raw,
        pydantic_model=PrivateUser
    )

    return user_obj


async def fetch_public_users(users_ids: list[int]) -> list[PublicUser]:
    await verify_users_is_existed(users_ids=users_ids)

    raw_users = await fetch_users_from_db(users_ids=users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def fetch_private_users(users_ids: list[int]) -> list[PrivateUser]:
    raw_users = await fetch_users_from_db(users_ids=users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PrivateUser
    )

    return users_objs


async def search_users_by_nickname(search_query: str, limit: int | None) -> list[PublicUser]:
    raw_users = await search_users_in_db(search_query=search_query, limit=limit)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def fetch_user_conversations(user_id: int) -> list[GetConversationsDB]:
    result = list()
    raw_user = await fetch_user_from_db(user_id=user_id)

    for conversation_obj in raw_user.conversations:
        members_ids = list()

        for member in conversation_obj.members:
            if member.id == user_id:
                continue
            members_ids.append(member.id)

        part_obj = GetConversations.model_validate(conversation_obj, from_attributes=True)
        full_obj = GetConversationsDB(
            members_ids=members_ids,
            **part_obj.model_dump()
        )
        result.append(full_obj)

    return result


async def update_user_profile(user_id: int, profile_data: UpdateUser) -> None:
    update_user_obj = UpdateUserDB(**profile_data.model_dump())
    if profile_data.password is not None:
        update_user_obj.password_hash = Hash.hash_password(profile_data.password)

    await update_user_in_db(user_id, update_user_obj)


async def upload_user_avatar(user_id: int, avatar_data: Avatar) -> None:

    async def save_avatar_to_file():
        await FileManager().validate_file(
            file_content=avatar_data.file,
            file_type=avatar_data.content_type,
            file_type_filter=MessagesTypes.IMAGE
        )
        avatar_save_path = MediaPatches.USERS_AVATARS_FOLDER.value / avatar_name
        await FileManager().write_file(file_path=avatar_save_path, file_data=avatar_data.file)

    avatar_name = f"{user_id}.{avatar_data.file_name.split('.')[-1]}"
    await save_avatar_to_file()
    await update_user_in_db(
        user_id=user_id,
        user_data=UpdateUserDB(
            avatar_name=avatar_name,
            avatar_type=avatar_data.content_type
        )
    )


async def fetch_user_avatar_metadata(user_id: int) -> dict[str, any]:
    await verify_user_is_existed(user_id=user_id)

    user_obj = await fetch_private_user(user_id=user_id)
    filepath = MediaPatches.USERS_AVATARS_FOLDER.value / f"{user_obj.avatar_name}"
    if not await FileManager().file_exists(file_path=filepath):
        raise FileNotFound()

    return {
        "file_path": filepath,
        "file_type": user_obj.avatar_type
    }


async def fetch_users_avatars_paths(users_ids: list[int]) -> list[Path]:
    avatars_paths = list()
    await verify_users_is_existed(users_ids=users_ids)

    users_objects = await fetch_private_users(users_ids=users_ids)
    for user_obj in users_objects:
        if user_obj.avatar_name is None:
            continue

        avatars_paths.append(MediaPatches.USERS_AVATARS_FOLDER.value / user_obj.avatar_name)

    if not avatars_paths:
        raise FileNotFound()

    return avatars_paths


async def fetch_user_unread_messages(user_id: int) -> list[GetUnreadMessages]:
    raw_user_data = await fetch_user_from_db(user_id=user_id)
    unread_messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_user_data.unread_messages,
        pydantic_model=GetUnreadMessages
    )
    for unread_message_obj in unread_messages_objs:
        await mark_message_delivered(message_id=unread_message_obj.message_id)
    return unread_messages_objs


async def remove_user_avatar(user_id: int, avatar_path: Path) -> None:
    await FileManager().delete_file(file_path=avatar_path)
    await delete_user_avatar_in_db(user_id=user_id)


async def fetch_users_online_status(users_ids: list[int]) -> list[UserOnline] | list:
    users_objs = list()
    not_founded_users_ids = list()

    for user_id in users_ids:
        user_last_online = await redis_client.get(f"user:last_online:{user_id}")
        if user_last_online:
            users_objs.append(
                UserOnline(
                    user_id=user_id,
                    last_online=user_last_online
                )
            )
        else:
            not_founded_users_ids.append(user_id)

    if not_founded_users_ids:
        raw_users_data = await get_users_last_online_from_db(users_ids=not_founded_users_ids)

        for raw_user_data in raw_users_data:
            transformed_data = {
                "user_id": raw_user_data[0],
                "last_online": raw_user_data[1]
            }
            users_objs.append(UserOnline.model_validate(transformed_data))

    return users_objs


async def delete_user_avatar(user_id: int):
    file_path = await fetch_user_avatar_metadata(user_id=user_id)
    await FileManager().delete_file(file_path=file_path["file_path"])


async def remove_user_account(user_id: int) -> None:
    user_obj = await fetch_user_from_db(user_id=user_id)
    for conversation_obj in user_obj.conversations:
        if conversation_obj.type == ConversationTypes.PRIVATE:
            messages_ids = await get_conversation_messages_id(conversation_id=conversation_obj.id)
            await remove_media_messages(user_id=user_id, messages_ids=messages_ids)

            await delete_conversation_in_db(conversation_id=conversation_obj.id)
        else:
            await leave_group(user_id=user_id, group_id=conversation_obj.id, delete_messages=True)

    await delete_user_avatar(user_id=user_id)
    await delete_user_from_db(user_id=user_id)
