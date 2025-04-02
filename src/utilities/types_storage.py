from sqlalchemy import text
from sqlalchemy.orm import mapped_column
from datetime import datetime
from typing import Annotated
from enum import Enum

from .secrets_config import generic_settings


datetime_required_type = Annotated[datetime, mapped_column(nullable=False)]
datetime_auto_set = Annotated[datetime, mapped_column(nullable=False, server_default=text("TIMEZONE('utc', now())"))]
datetime_not_required_type = Annotated[datetime, mapped_column(nullable=True)]
datetime_auto_update = Annotated[datetime, mapped_column(nullable=True, onupdate=text("TIMEZONE('utc', now())"))]

text_required_type = Annotated[str, mapped_column(nullable=False)]
text_not_required_type = Annotated[str, mapped_column(nullable=True)]

primary_key_type = Annotated[int, mapped_column(primary_key=True)]


class ConversationMemberRoles(str, Enum):
    CREATOR = 'creator'
    ADMIN = "admin"
    MEMBER = "member"


class ConversationTypes(str, Enum):
    PRIVATE = 'private'
    GROUP = 'group'


class MessagesStatus(str, Enum):
    CREATED = 'created'
    SENT = 'sent'
    DELIVERED = 'delivered'
    READ = 'read'


class MessagesTypes(str, Enum):
    TEXT = 'text'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    FILE = 'file'
    VOICE = 'voice'


class EntitiesTypes(Enum):
    MESSAGES = 'message'
    CALLS = 'call'


class CallsStatus(str, Enum):
    PENDING = 'pending'
    COMING = 'coming'
    COMPLETED = 'completed'
    MISSED = 'missed'


class MediaPatches(Enum):
    USERS_AVATARS_FOLDER = generic_settings.MEDIA_FOLDER / "users" / "avatars"
    GROUPS_AVATARS_FOLDER = generic_settings.MEDIA_FOLDER / "groups" / "avatars"
    MEDIA_MESSAGES_FOLDER = generic_settings.MEDIA_FOLDER / "messages" / "media"


class AppModes(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"
