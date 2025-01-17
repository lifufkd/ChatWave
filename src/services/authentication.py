from sqlalchemy.exc import IntegrityError
from schemas import AuthorizeUser, CreateUser, CreateUserExtended
from repository import get_user_by_username_from_db, insert_user_in_db
from utilities import Hash, JWT, UserNotFoundError, InvalidPasswordError, UserAlreadyExists


async def get_access_token(request_data: AuthorizeUser) -> str:
    user_data = await get_user_by_username_from_db(request_data)

    if not user_data:
        raise UserNotFoundError()

    request_data.id = user_data[0]
    request_data.password_hash = user_data[1]

    if not Hash.verify_password(plain_password=request_data.password, hashed_password=request_data.password_hash):
        raise InvalidPasswordError()

    access_token = JWT.create_token(
        {
            "id": request_data.id
        }
    )

    return access_token


async def add_user(request_data: CreateUser) -> None:
    user_obj = CreateUserExtended(**request_data.model_dump())
    user_obj.password_hash = Hash.hash_password(user_obj.password)
    try:
        await insert_user_in_db(user_obj)
    except IntegrityError:
        raise UserAlreadyExists()


