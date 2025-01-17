from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_cache.decorator import cache
from typing import Annotated

from schemas import PrivateUser, UpdateUser, PublicUser, SearchUser, Avatars, UserOnline, UserOnlineExtended
from dependencies import verify_token, process_user_last_online_update
from services import get_profile, update_profile, get_profiles, update_avatar, get_avatars, users_online
from utilities import InvalidFileType, FIleToBig, ImageCorrupted, generic_settings, FileManager

users_router = APIRouter(
    tags=["Users"],
    prefix="/users",
    dependencies=[Depends(process_user_last_online_update)]
)

anonymous_users_router = APIRouter(
    tags=["Users"],
    prefix="/users"
)


@users_router.get("/my_profile", status_code=status.HTTP_200_OK, response_model=PrivateUser)
async def my_profile_endpoint(current_user_id: Annotated[int, Depends(verify_token)]):
    profile_data = await get_profile(current_user_id)

    return profile_data


@users_router.put("/update_profile", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile_endpoint(current_user_id: Annotated[int, Depends(verify_token)], profile_data: UpdateUser):
    await update_profile(user_id=current_user_id, profile=profile_data)


@users_router.put("/update_avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile_endpoint(current_user_id: Annotated[int, Depends(verify_token)], avatar: UploadFile = File()):
    try:
        await update_avatar(user_id=current_user_id, avatar=avatar)
    except InvalidFileType as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FIleToBig as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ImageCorrupted as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@anonymous_users_router.get("/avatar/{user_id}", status_code=status.HTTP_200_OK)
async def avatar_endpoint(user_id: str):
    filepath = generic_settings.MEDIA_FOLDER / "avatars" / user_id
    if not FileManager.file_exists(path=filepath):
        raise HTTPException(status_code=404, detail="Avatar not found")
    return FileResponse(str(filepath))


@anonymous_users_router.post("/avatars", status_code=status.HTTP_200_OK)
async def avatars_endpoint(avatars: Avatars):
    zip_obj = await get_avatars(avatars.users_ids)
    return StreamingResponse(zip_obj, media_type="application/zip")


@anonymous_users_router.post("/users_profiles", status_code=status.HTTP_200_OK, response_model=list[PublicUser])
async def users_profiles_endpoint(search_params: SearchUser):
    profile_data = await get_profiles(search_params=search_params)

    return profile_data


@anonymous_users_router.post("/users_last_online", status_code=status.HTTP_200_OK, response_model=list[UserOnlineExtended])
async def users_last_online_endpoint(users_ids: UserOnline):
    return await users_online(user_ids=users_ids)

