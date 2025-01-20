from sqlalchemy import text
from sqlalchemy.orm import mapped_column
from datetime import datetime
from typing import Annotated
from enum import Enum


datetime_required_type = Annotated[datetime, mapped_column(nullable=False)]
datetime_auto_set = Annotated[datetime, mapped_column(nullable=False, server_default=text("TIMEZONE('utc', now())"))]
datetime_not_required_type = Annotated[datetime, mapped_column(nullable=True)]
datetime_auto_update = Annotated[datetime, mapped_column(nullable=True, onupdate=text("TIMEZONE('utc', now())"))]

text_required_type = Annotated[str, mapped_column(nullable=False)]
text_not_required_type = Annotated[str, mapped_column(nullable=True)]

primary_key_type = Annotated[int, mapped_column(primary_key=True)]


class ConversationMemberRoles(Enum):
    CREATOR = 'CREATOR'
    ADMIN = "admin"
    MEMBER = "member"


class ConversationTypes(Enum):
    PRIVATE = 'private'
    GROUP = 'group'


class MessagesStatus(Enum):
    CREATED = 'created'
    SENT = 'sent'
    DELIVERED = 'delivered'
    READ = 'read'


class MessagesTypes(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    FILE = 'file'
    VOICE = 'voice'


class CallsStatus(Enum):
    PENDING = 'pending'
    COMING = 'coming'
    COMPLETED = 'completed'
    MISSED = 'missed'
