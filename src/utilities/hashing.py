from jose import jwt
from passlib import context
from datetime import datetime, timedelta

from utilities import jwt_settings


crypt_context = context.CryptContext(schemes=["bcrypt"], deprecated='auto')


class Hash:

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return crypt_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return crypt_context.verify(plain_password, hashed_password)


class JWT:

    @staticmethod
    def create_token(payload: dict) -> str:
        copied_payload = payload.copy()
        copied_payload.update({'exp': datetime.utcnow() + timedelta(days=jwt_settings.JWT_ACCESS_TOKEN_EXPIRES)})
        token = jwt.encode(copied_payload, key=jwt_settings.JWT_ALGORITHM, algorithm=jwt_settings.JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        payload = jwt.decode(token=token, key=jwt_settings.JWT_ALGORITHM, algorithms=[jwt_settings.JWT_ALGORITHM])
        return payload
