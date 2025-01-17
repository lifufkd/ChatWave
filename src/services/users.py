from fastapi import UploadFile
from sqlalchemy import text
from repository import get_private_user, update_user, get_public_users, get_users_online
from schemas import PrivateUser, UpdateUser, PublicUser, SearchUser, UpdateUserExtended, UserOnlineExtended, UserOnline
from utilities import sqlalchemy_to_pydantic, many_sqlalchemy_to_pydantic, FileManager, generic_settings, Hash
from io import BytesIO


async def get_profile(user_id: int) -> PrivateUser:
    user_raw = await get_private_user(user_id)
    user_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=user_raw,
        pydantic_model=PrivateUser
    )

    return user_obj


async def get_profiles(search_params: SearchUser) -> list[PublicUser]:
    raw_users = await get_public_users(search_params=search_params)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def update_profile(user_id: int, profile: UpdateUser) -> None:
    user_extended_obj = UpdateUserExtended(**profile.model_dump())
    if profile.password is not None:
        user_extended_obj.password_hash = Hash.hash_password(profile.password)

    await update_user(user_id, user_extended_obj)


async def update_avatar(user_id: int, avatar: UploadFile) -> None:
    async def _update_avatar():
        if avatar is not None:
            FileManager.validate_image(file=avatar)
            avatar_save_path = generic_settings.MEDIA_FOLDER / "avatars" / str(user_id)
            FileManager.write_file(path=avatar_save_path, content=await avatar.read())

    await _update_avatar()


async def get_avatars(users_ids: list[int]) -> BytesIO:
    avatars_paths = [generic_settings.MEDIA_FOLDER / "avatars" / str(user_id) for user_id in users_ids]
    zip_obj = FileManager().archive_files(paths=avatars_paths)
    return zip_obj


async def users_online(user_ids: UserOnline) -> list[UserOnlineExtended]:
    raw_data = await get_users_online(users=user_ids)
    users_objs = list()
    for item in raw_data:
        transformed_data = {
            "user_id": item[0],
            "last_online": item[1]
        }
        users_objs.append(UserOnlineExtended.model_validate(transformed_data))

    return users_objs
