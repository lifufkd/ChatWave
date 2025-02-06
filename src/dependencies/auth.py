from typing import Annotated
from fastapi import Depends, WebSocket
from jose import JWTError

from utilities import oauth2_scheme, JWT, InvalidCredentials


async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        token_payload = JWT.decode_token(token)
        user_id = token_payload['id']
        if user_id is None:
            raise InvalidCredentials()
    except JWTError:
        raise InvalidCredentials()

    return user_id


async def verify_token_ws(token: str) -> int | None:
    try:
        token_payload = JWT.decode_token(token)
        user_id = token_payload['id']
        if user_id is None:
            return None
    except JWTError:
        return None

    return user_id
