from sqlalchemy.exc import IntegrityError
from schemas import AuthorizeUser, CreateUser, CreateUserExtended
from repository import authorize_user, register_user
from utilities import Hash, JWT, UserNotFoundError, InvalidPasswordError, UserAlreadyExists


async def login(request_data: AuthorizeUser) -> str:
    user_found = await authorize_user(request_data)
    if not user_found:
        raise UserNotFoundError()

    if not Hash.verify_password(plain_password=request_data.password, hashed_password=request_data.password_hash):
        raise InvalidPasswordError()

    access_token = JWT.create_token(
        {
            "id": request_data.id
        }
    )

    return access_token


async def signup(request_data: CreateUser) -> None:
    user_obj = CreateUserExtended(**request_data.model_dump())
    user_obj.password_hash = Hash.hash_password(user_obj.password)
    try:
        await register_user(user_obj)
    except IntegrityError:
        raise UserAlreadyExists()


