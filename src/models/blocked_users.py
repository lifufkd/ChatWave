from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import OrmBase
from utilities import datetime_required_type


class BlockedUsers(OrmBase):
    __tablename__ = 'blocked_users'
    blocker_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    blocked_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True
    )
    created_at: Mapped[datetime_required_type]


