import re
from utilities import generic_settings
from pydantic import BaseModel, model_validator


def validate_password(value: str) -> str | None:
    if value is None:
        return value

    if not re.search(r'[a-z]', value):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[A-Z]', value):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[0-9]', value):
        raise ValueError('Password must contain at least one digit')

    return value


def validate_nicknames(value: str) -> str | None:
    if value is not None:
        if len(value) < 3 or len(value) > 128:
            raise ValueError('Nicknames must be between 3 and 128 characters long')
    return value


def request_limit(values: list[any]) -> list[any]:
    if values is not None:
        if len(values) > generic_settings.MAX_ITEMS_PER_REQUEST:
            raise ValueError(f'Request limit must be less than {generic_settings.MAX_ITEMS_PER_REQUEST} characters')

    return values


def check_exclusive_fields(values):
    message_id, call_id = values.get("message_id"), values.get("call_id")
    if message_id is None and call_id is None:
        raise ValueError("Either 'message_id' or 'call_id' must be provided")
    if message_id is not None and call_id is not None:
        raise ValueError("Only one of 'message_id' or 'call_id' must be provided")
    return values


class ValidateModelNotEmpty(BaseModel):
    @model_validator(mode="before")
    def validate_not_empty(cls, values: dict[str, any]) -> dict[str, any]:
        if not any(values.values()):
            raise ValueError("At least one field must be filled.")
        return values
