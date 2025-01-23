from pathlib import Path
from fastapi import UploadFile
from repository import (
    update_user_in_db,
    get_users_by_nickname_from_db,
    get_users_online_from_db,
    delete_user_avatar_in_db,
    get_user_from_db,
    get_users_from_db
)
from schemas import (
    PrivateUser,
    UpdateUser,
    PublicUser,
    SearchUser,
    UpdateUserExtended,
    UserOnlineExtended,
    UserOnline,
    GetUsers, GetConversations, GetConversationsExtended
)
from utilities import (
    sqlalchemy_to_pydantic,
    many_sqlalchemy_to_pydantic,
    FileManager,
    generic_settings,
    Hash,
    FileNotFound,
    MessagesTypes
)


async def get_public_user(user_id: int) -> PublicUser:
    user_raw = await get_user_from_db(user_id=user_id)
    user_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=user_raw,
        pydantic_model=PublicUser
    )

    return user_obj


async def get_private_user(user_id: int) -> PrivateUser:
    user_raw = await get_user_from_db(user_id=user_id)
    user_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=user_raw,
        pydantic_model=PrivateUser
    )

    return user_obj


async def get_public_users(request_obj: GetUsers) -> list[PublicUser]:
    raw_users = await get_users_from_db(users_ids=request_obj.users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def get_private_users(request_obj: GetUsers) -> list[PrivateUser]:
    raw_users = await get_users_from_db(users_ids=request_obj.users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PrivateUser
    )

    return users_objs


async def process_search_users(request_obj: SearchUser) -> list[PublicUser]:
    raw_users = await get_users_by_nickname_from_db(search_params=request_obj)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def get_conversations(current_user_id: int) -> list[GetConversationsExtended]:
    result = list()
    raw_user = await get_user_from_db(user_id=current_user_id)

    for conversation_obj in raw_user.conversations:
        members_ids = list()

        for member in conversation_obj.members:
            if member.id == current_user_id:
                continue
            members_ids.append(member.id)

        part_obj = GetConversations.model_validate(conversation_obj, from_attributes=True)
        full_obj = GetConversationsExtended(
            members_ids=members_ids,
            **part_obj.model_dump()
        )
        result.append(full_obj)

    return result


async def update_profile(user_id: int, profile: UpdateUser) -> None:
    user_extended_obj = UpdateUserExtended(**profile.model_dump())
    if profile.password is not None:
        user_extended_obj.password_hash = Hash.hash_password(profile.password)

    await update_user_in_db(user_id, user_extended_obj)


async def update_avatar(user_id: int, avatar: UploadFile) -> None:

    async def save_avatar_to_file():
        FileManager().validate_file(
            file_content=await avatar.read(),
            file_type=avatar.content_type,
            file_type_filter=MessagesTypes.IMAGE
        )
        avatar_save_path = generic_settings.MEDIA_FOLDER / "avatars" / avatar_name
        FileManager.write_file(path=avatar_save_path, content=await avatar.read())

    avatar_name = f"{user_id}.{avatar.filename.split('.')[-1]}"
    await save_avatar_to_file()
    await update_user_in_db(
        user_id=user_id,
        user_data=UpdateUserExtended(
            avatar_name=avatar_name,
            avatar_type=avatar.content_type
        )
    )


async def get_avatar_path(user_id: int) -> Path:
    user_obj = await get_private_user(user_id=user_id)
    filepath = generic_settings.MEDIA_FOLDER / "avatars" / f"{user_obj.avatar_name}"
    if not FileManager.file_exists(path=filepath):
        raise FileNotFound()

    return filepath


async def get_avatars_paths(users_ids: list[int]) -> list[Path]:
    avatars_paths = list()
    avatar_base_path = generic_settings.MEDIA_FOLDER / "avatars"
    users_objects = await get_private_users(
        request_obj=GetUsers(
            users_ids=users_ids
        )
    )
    for user_obj in users_objects:
        if user_obj.avatar_name is None:
            continue

        avatars_paths.append(avatar_base_path / user_obj.avatar_name)

    if not avatars_paths:
        raise FileNotFound()

    return avatars_paths


async def delete_avatar(user_id: int, avatar_path: Path) -> None:
    FileManager.delete_file(path=avatar_path)
    await delete_user_avatar_in_db(user_id=user_id)


async def users_online(user_ids: UserOnline) -> list[UserOnlineExtended]:
    raw_data = await get_users_online_from_db(users=user_ids)
    users_objs = list()
    for item in raw_data:
        transformed_data = {
            "user_id": item[0],
            "last_online": item[1]
        }
        users_objs.append(UserOnlineExtended.model_validate(transformed_data))

    return users_objs
