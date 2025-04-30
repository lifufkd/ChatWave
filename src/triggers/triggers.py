from sqlalchemy import text

from database import session
from utilities import db_settings


async def setup_unread_messages_changes_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION unread_messages_changes()
                RETURNS TRIGGER AS $$
                DECLARE
                    user_id INTEGER;
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        user_id := NEW.user_id;
                        PERFORM pg_notify('unread_messages_changes', user_id::text);
                    END IF;

                    IF TG_OP = 'DELETE' THEN
                        user_id := OLD.user_id;
                        PERFORM pg_notify('unread_messages_changes', user_id::text);
                    END IF;

                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )
        await cursor.execute(
            text(f"DROP TRIGGER IF EXISTS unread_messages_trigger ON {db_settings.DB_SCHEMA}.unread_messages")
        )
        await cursor.execute(
            text(f"""
                CREATE TRIGGER unread_messages_trigger
                AFTER INSERT OR DELETE ON {db_settings.DB_SCHEMA}.unread_messages
                FOR EACH ROW
                EXECUTE FUNCTION unread_messages_changes()
            """)
        )

        await cursor.commit()


async def setup_recipients_change_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION recipients_change()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        PERFORM pg_notify(
                            'recipients_change',
                            json_build_object(
                                'user_id', NEW.user_id,
                                'conversation_id', NEW.conversation_id
                            )::text
                        );
                    ELSIF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify(
                            'recipients_change',
                            json_build_object(
                                'user_id', OLD.user_id,
                                'conversation_id', OLD.conversation_id
                            )::text
                        );
                    END IF;
                
                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )
        await cursor.execute(
            text(f"DROP TRIGGER IF EXISTS recipients_change_trigger ON {db_settings.DB_SCHEMA}.conversations_members")
        )
        await cursor.execute(
            text(f"""
                CREATE TRIGGER recipients_change_trigger
                AFTER INSERT OR DELETE ON {db_settings.DB_SCHEMA}.conversations_members
                FOR EACH ROW
                EXECUTE FUNCTION recipients_change()
            """)
        )

        await cursor.commit()


async def setup_user_delete_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION user_delete()
                RETURNS TRIGGER AS $$
                DECLARE
                    avatar_name TEXT;
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        avatar_name := OLD.avatar_name;
                        PERFORM pg_notify('user_delete', avatar_name::text);
                    END IF;

                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )
        await cursor.execute(
            text(f"DROP TRIGGER IF EXISTS user_delete_trigger ON {db_settings.DB_SCHEMA}.users")
        )
        await cursor.execute(
            text(f"""
                CREATE TRIGGER user_delete_trigger
                AFTER DELETE ON {db_settings.DB_SCHEMA}.users
                FOR EACH ROW
                EXECUTE FUNCTION user_delete()
            """)
        )

        await cursor.commit()


async def setup_conversation_delete_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION conversation_delete()
                RETURNS TRIGGER AS $$
                DECLARE
                    avatar_name TEXT;
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        avatar_name := OLD.avatar_name;
                        PERFORM pg_notify('conversation_delete', avatar_name::text);
                    END IF;

                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )
        await cursor.execute(
            text(f"DROP TRIGGER IF EXISTS conversation_delete_trigger ON {db_settings.DB_SCHEMA}.conversations")
        )
        await cursor.execute(
            text(f"""
                CREATE TRIGGER conversation_delete_trigger
                AFTER DELETE ON {db_settings.DB_SCHEMA}.conversations
                FOR EACH ROW
                EXECUTE FUNCTION conversation_delete()
            """)
        )

        await cursor.commit()


async def setup_messages_delete_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION messages_delete()
                RETURNS TRIGGER AS $$
                DECLARE
                    file_content_name TEXT;
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        file_content_name := OLD.file_content_name;
                        PERFORM pg_notify('messages_delete', file_content_name::text);
                    END IF;

                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
            """)
        )
        await cursor.execute(
            text(f"DROP TRIGGER IF EXISTS messages_delete_trigger ON {db_settings.DB_SCHEMA}.messages")
        )
        await cursor.execute(
            text(f"""
                CREATE TRIGGER messages_delete_trigger
                AFTER DELETE ON {db_settings.DB_SCHEMA}.messages
                FOR EACH ROW
                EXECUTE FUNCTION messages_delete()
            """)
        )

        await cursor.commit()
