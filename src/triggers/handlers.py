import json

from dependencies import redis_client


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
