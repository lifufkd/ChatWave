import json
from pathlib import Path
from fastapi import WebSocket, WebSocketDisconnect

from dependencies import redis_client
from repository import (
    update_user,
    select_users_by_nickname,
    select_users_last_online,
    delete_user_avatar,
    select_user,
    select_users,
    delete_conversation,
    delete_user,
    is_user_exists,
    select_conversation_member_role
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
    GetConversationsWithMembers,
    GetUnreadMessages,
    UserRole
)
from .messages import mark_message_delivered
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
    user_raw = await select_user(user_id=user_id)
    user_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=user_raw,
        pydantic_model=PrivateUser
    )

    return user_obj


async def fetch_public_users(users_ids: list[int]) -> list[PublicUser]:
    await verify_users_is_existed(users_ids=users_ids)

    raw_users = await select_users(users_ids=users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def fetch_private_users(users_ids: list[int]) -> list[PrivateUser]:
    raw_users = await select_users(users_ids=users_ids)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PrivateUser
    )

    return users_objs


async def search_users_by_nickname(search_query: str, limit: int | None) -> list[PublicUser]:
    raw_users = await select_users_by_nickname(search_query=search_query, limit=limit)
    users_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_users,
        pydantic_model=PublicUser
    )

    return users_objs


async def fetch_user_conversations(user_id: int) -> list[GetConversationsWithMembers]:
    result = list()
    raw_user = await select_user(user_id=user_id)

    for conversation_obj in raw_user.conversations:
        members = list()

        for member in conversation_obj.members:
            if member.id == user_id:
                continue
            member_role_in_group = await select_conversation_member_role(
                user_id=member.id,
                conversation_id=conversation_obj.id
            )
            members.append(
                UserRole(
                    user_id=member.id,
                    user_role=member_role_in_group
                )
            )

        part_obj = GetConversations.model_validate(conversation_obj, from_attributes=True)
        full_obj = GetConversationsWithMembers(
            members=members,
            **part_obj.model_dump()
        )
        result.append(full_obj)

    return result


async def fetch_user_conversations_ids(user_id: int) -> list[int]:
    result = list()

    raw_user = await select_user(user_id=user_id)
    for conversation_obj in raw_user.conversations:
        result.append(conversation_obj.id)

    return result


async def update_user_profile(user_id: int, profile_data: UpdateUser) -> None:
    update_user_obj = UpdateUserDB(**profile_data.model_dump())
    if profile_data.password is not None:
        update_user_obj.password_hash = Hash.hash_password(profile_data.password)

    await update_user(user_id, update_user_obj)


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
    await update_user(
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
    raw_user_data = await select_user(user_id=user_id)
    unread_messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_user_data.unread_messages,
        pydantic_model=GetUnreadMessages
    )
    for unread_message_obj in unread_messages_objs:
        await mark_message_delivered(message_id=unread_message_obj.message_id)
    return unread_messages_objs


async def remove_user_avatar(user_id: int, avatar_path: Path) -> None:
    await delete_user_avatar(user_id=user_id)
    await FileManager().delete_file(file_path=avatar_path)


async def fetch_user_recipients_last_online(user_id: int) -> list[int]:
    users_ids = list()

    raw_user = await select_user(user_id=user_id)
    for conversation_obj in raw_user.conversations:
        for member in conversation_obj.members:
            if member.id == user_id:
                continue
            users_ids.append(member.id)

    return list(set(users_ids))


async def fetch_users_online_status(users_ids: list[int]) -> list[UserOnline]:
    users_objs = list()
    raw_users_data = await select_users_last_online(users_ids=users_ids)

    for raw_user_data in raw_users_data:
        transformed_data = {
            "user_id": raw_user_data[0],
            "last_online": raw_user_data[1]
        }
        users_objs.append(UserOnline.model_validate(transformed_data))

    return users_objs


async def remove_user_account(user_id: int) -> None:
    user_obj = await select_user(user_id=user_id)
    for conversation_obj in user_obj.conversations:
        if conversation_obj.type == ConversationTypes.PRIVATE:
            await delete_conversation(conversation_id=conversation_obj.id)
        else:
            await leave_group(user_id=user_id, group_id=conversation_obj.id, delete_messages=True)

    await delete_user(user_id=user_id)


async def unread_messages_listener(current_user_id: int, websocket: WebSocket) -> None:
    async def send_user_unread_messages():
        result = list()
        for unread_message_obj in unread_messages_objs:
            result.append(
                {
                    **unread_message_obj.model_dump()
                }
            )
        for unread_message_obj in unread_messages_objs:
            await mark_message_delivered(message_id=unread_message_obj.message_id)
        await websocket.send_json(result)

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("user:unread_messages_events")

    unread_messages_objs = await fetch_user_unread_messages(user_id=current_user_id)
    await send_user_unread_messages()

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            payload = message["data"].decode()
            event_id = int(payload)
            if event_id != current_user_id:
                continue

            if not (await is_user_exists(user_id=current_user_id)):
                await websocket.close(code=1008)
                break

            unread_messages_objs = await fetch_user_unread_messages(user_id=current_user_id)

            await send_user_unread_messages()
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("user:unread_messages")


async def user_last_online_listener(current_user_id: int, websocket: WebSocket) -> None:
    async def send_recipients_last_online():
        result = list()
        for user_online_obj in recipients_last_online_objs:
            if user_online_obj.last_online is None:
                user_last_online = None
            else:
                user_last_online = user_online_obj.last_online.strftime("%Y-%m-%d %H:%M:%S")

            result.append(
                {
                    "user_id": user_online_obj.user_id,
                    "last_online": user_last_online
                }
            )

        await websocket.send_json(result)

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("user:last_online_events", "user:recipients_change_events")

    user_conversations_ids = await fetch_user_conversations_ids(user_id=current_user_id)
    user_recipients_ids = await fetch_user_recipients_last_online(user_id=current_user_id)
    recipients_last_online_objs = await fetch_users_online_status(users_ids=user_recipients_ids)
    await send_recipients_last_online()

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"].decode()
            payload = message["data"].decode()

            match channel:
                case "user:recipients_change_events":
                    event_data = json.loads(payload)
                    event_user_id = int(event_data.get("user_id"))
                    event_conversation_id = int(event_data.get("conversation_id"))
                    if event_conversation_id not in user_conversations_ids and event_user_id != current_user_id:
                        continue

                    if not (await is_user_exists(user_id=current_user_id)):
                        await websocket.close(code=1008)
                        break

                    temp_user_conversations_ids = await fetch_user_conversations_ids(user_id=current_user_id)
                    temp_user_recipients_ids = await fetch_user_recipients_last_online(user_id=current_user_id)
                    new_recipients_ids = list(set(temp_user_recipients_ids)-set(user_recipients_ids))
                    deleted_recipients_ids = list(set(user_recipients_ids)-set(temp_user_recipients_ids))
                    if new_recipients_ids:
                        recipients_last_online_objs.extend(
                            await fetch_users_online_status(users_ids=new_recipients_ids)
                        )
                    if deleted_recipients_ids:
                        for recipient_last_online_obj in recipients_last_online_objs:
                            if recipient_last_online_obj.user_id not in deleted_recipients_ids:
                                continue
                            recipients_last_online_objs.remove(recipient_last_online_obj)

                    user_conversations_ids = temp_user_conversations_ids.copy()
                    user_recipients_ids = temp_user_recipients_ids.copy()
                    await send_recipients_last_online()

                case "user:last_online_events":
                    event_user_id = int(payload)
                    if event_user_id not in user_recipients_ids:
                        continue

                    if not (await is_user_exists(user_id=current_user_id)):
                        await websocket.close(code=1008)
                        break

                    for recipient_last_online_obj in recipients_last_online_objs:
                        if recipient_last_online_obj.user_id != event_user_id:
                            continue
                        recipients_last_online_objs.remove(recipient_last_online_obj)
                        recipients_last_online_objs.extend(
                            await fetch_users_online_status(users_ids=[event_user_id])
                        )

                    await send_recipients_last_online()
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("user:last_online_events", "user:recipients_change_events")
