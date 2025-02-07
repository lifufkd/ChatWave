import json

from dependencies import redis_client
from storage import FileManager
from utilities import MediaPatches


async def handle_unread_messages_changes(payload: str):
    row_data = json.loads(payload)
    await redis_client.publish("user:unread_messages_events", str(row_data.get("user_id")))


async def handle_recipients_change(payload: str):
    row_data = json.loads(payload)
    data = json.dumps(
        {
            "user_id": row_data.get("user_id"),
            "conversation_id": row_data.get("conversation_id"),
        }
    )
    await redis_client.publish("user:recipients_change_events", data)


async def handle_user_delete_changes(payload: str):
    row_data = json.loads(payload)
    file_manager = FileManager()
    filepath = MediaPatches.USERS_AVATARS_FOLDER.value / f"{row_data.get('avatar_name')}"

    if row_data.get('avatar_name') is None:
        return None
    if not (await file_manager.file_exists(file_path=filepath)):
        return None

    await file_manager.delete_file(file_path=filepath)


async def handle_conversation_delete_changes(payload: str):
    row_data = json.loads(payload)
    file_manager = FileManager()
    filepath = MediaPatches.GROUPS_AVATARS_FOLDER.value / f"{row_data.get('avatar_name')}"

    if row_data.get('avatar_name') is None:
        return None
    if not (await file_manager.file_exists(file_path=filepath)):
        return None

    await file_manager.delete_file(file_path=filepath)


async def handle_messages_delete_changes(payload: str):
    row_data = json.loads(payload)
    file_manager = FileManager()
    filepath = MediaPatches.MEDIA_MESSAGES_FOLDER.value / f"{row_data.get('file_content_name')}"

    if row_data.get('file_content_name') is None:
        return None
    if not (await file_manager.file_exists(file_path=filepath)):
        return None

    await file_manager.delete_file(file_path=filepath)
