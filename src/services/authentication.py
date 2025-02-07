from sqlalchemy.exc import IntegrityError
from schemas import CreateUser, CreateUserDB
from repository import select_user_by_username, insert_user
from utilities import Hash, JWT, UserNotFoundError, InvalidPasswordError, UserAlreadyExists


async def get_access_token(username: str, password: str) -> str:
    user_data = await select_user_by_username(username)

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


async def create_user(request_data: CreateUser) -> None:
    new_user_obj = CreateUserDB(
        password_hash=Hash.hash_password(request_data.password),
        **request_data.model_dump()
    )
    try:
        await insert_user(new_user_obj)
    except IntegrityError:
        raise UserAlreadyExists()
