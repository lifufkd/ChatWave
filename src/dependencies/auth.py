from typing import Annotated
from fastapi import Depends
from jose import JWTError
from schemas import PublicUser

from utilities import oauth2_scheme, JWT, credential_exception


async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    try:
        token_payload = JWT.decode_token(token)
        user_id = token_payload['id']
        if user_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception

    return user_id


