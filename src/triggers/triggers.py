from sqlalchemy import text

from database import session


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
            text("DROP TRIGGER IF EXISTS unread_messages_trigger ON chatwave.unread_messages")
        )
        await cursor.execute(
            text("""
                CREATE TRIGGER unread_messages_trigger
                AFTER INSERT OR DELETE ON chatwave.unread_messages
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
            text("DROP TRIGGER IF EXISTS recipients_change_trigger ON chatwave.conversations_members")
        )
        await cursor.execute(
            text("""
                CREATE TRIGGER recipients_change_trigger
                AFTER INSERT OR DELETE ON chatwave.conversations_members
                FOR EACH ROW
                EXECUTE FUNCTION recipients_change()
            """)
        )

        await cursor.commit()
