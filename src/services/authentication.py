from sqlalchemy.exc import IntegrityError
from schemas import CreateUser, CreateUserDB
from repository import fetch_user_credentials_by_username, create_user_in_db
from utilities import Hash, JWT, UserNotFoundError, InvalidPasswordError, UserAlreadyExists


async def get_access_token(username: str, password: str) -> str:
    user_data = await fetch_user_credentials_by_username(username)

    if not user_data:
        raise UserNotFoundError()

    user_id = user_data[0]
    password_hash = user_data[1]

    if not Hash.verify_password(plain_password=password, hashed_password=password_hash):
        raise InvalidPasswordError()

    access_token = JWT.create_token(
        {
            "id": user_id
        }
    )

    return access_token


async def add_user(request_data: CreateUser) -> None:
    new_user_obj = CreateUserDB(
        password_hash=Hash.hash_password(request_data.password),
        **request_data.model_dump()
    )
    try:
        await create_user_in_db(new_user_obj)
    except IntegrityError:
        raise UserAlreadyExists()


