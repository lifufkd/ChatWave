from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import OrmBase
from utilities import ConversationMemberRoles, datetime_auto_set


class ConversationMembers(OrmBase):
    __tablename__ = 'conversations_members'
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        primary_key=True
    )

    role: Mapped[ConversationMemberRoles] = mapped_column(nullable=False)
    joined_at: Mapped[datetime_auto_set]

