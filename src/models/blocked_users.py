from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from database import OrmBase
from utilities import datetime_type


class BlockedUsers(OrmBase):
    __tablename__ = 'blocked_users'
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    blocker_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    blocked_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )
    created_at: Mapped[datetime_type]

    __table_args__ = (
        Index("ix_blocked_users_blocker_id_blocked_id", "blocker_id", "blocked_id"),
    )
