import re
from utilities import generic_settings


def validate_password(value: str) -> str | None:
    if value is None:
        return value

    if not re.search(r'[a-z]', value):  # минимум одна строчная буква
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[A-Z]', value):  # минимум одна прописная буква
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[0-9]', value):  # минимум одна цифра
        raise ValueError('Password must contain at least one digit')

    return value


def validate_nicknames(value: str) -> str | None:
    if value is not None:
        if len(value) < 3 or len(value) > 128:
            raise ValueError('Nicknames must be between 3 and 128 characters long')
    return value


def validate_nicknames_and_ids(values):
    nicknames = values.get('nickname')
    ids = values.get('ids')

    # Проверяем, что одно из полей заполнено, а другое нет
    if (nicknames and ids) or (not nicknames and not ids):
        raise ValueError("Only one of 'nickname' or 'ids' can be filled, and one must be filled.")

    return values


def request_limit(values: list[any]) -> list[any]:
    if values is not None:
        if len(values) > generic_settings.MAX_ITEMS_PER_REQUEST:
            raise ValueError(f'Request limit must be less than {generic_settings.MAX_ITEMS_PER_REQUEST} characters')

    return values

