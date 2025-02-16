import secrets
import os

from .config import YamlConfig


def generate_jwt_token() -> str:
    secret_key_env = os.getenv("JWT_SECRET_KEY")
    secret_key_yaml = YamlConfig().get_value(key="JWT_SECRET_KEY")
    if secret_key_env:
        return secret_key_env
    elif secret_key_yaml:
        return secret_key_yaml
    elif not secret_key_env and not secret_key_yaml:
        secret_key = secrets.token_hex(32)
        YamlConfig().add_value(key="JWT_SECRET_KEY", value=secret_key)
        with open(".env", "a") as f:
            f.write(f"\nJWT_SECRET_KEY={secret_key}")

    return secret_key
