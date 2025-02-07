from sqlalchemy import text

from database import session
from utilities import db_settings


async def setup_unread_messages_changes_trigger():
    async with session() as cursor:
        await cursor.execute(
            text("""
                CREATE OR REPLACE FUNCTION unread_messages_changes()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF TG_OP = 'INSERT' THEN
                        PERFORM pg_notify('unread_messages_changes', row_to_json(NEW)::text);
                    END IF;

                    IF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify('unread_messages_changes', row_to_json(OLD)::text);
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
                        PERFORM pg_notify('recipients_change', row_to_json(NEW)::text);
                    END IF;

                    IF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify('recipients_change', row_to_json(OLD)::text);
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
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify('user_delete', row_to_json(OLD)::text);
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
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify('conversation_delete', row_to_json(OLD)::text);
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
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        PERFORM pg_notify('messages_delete', row_to_json(OLD)::text);
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
