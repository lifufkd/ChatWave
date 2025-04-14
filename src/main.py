import asyncio

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from triggers import (
    setup_unread_messages_changes_trigger,
    setup_unread_messages_changes_listener,
    setup_recipients_change_trigger,
    setup_recipients_change_listener,
    setup_user_delete_trigger,
    setup_conversation_delete_trigger,
    setup_messages_delete_trigger,
    setup_user_delete_listener,
    setup_conversation_delete_listener,
    setup_messages_delete_listener
)
from repository import create_tables, create_schema
from routes import (
    authorization_router,
    users_router,
    conversations_router,
    anonymous_users_router,
    messages_router
)
from storage import FileManager
from utilities import (
    UserNotFoundError,
    ConversationNotFoundError,
    AccessDeniedError,
    IsNotAGroupError,
    IsNotAChatError,
    InvalidPasswordError,
    InvalidCredentials,
    UserAlreadyExists,
    InvalidFileType,
    FIleToBig,
    ImageCorrupted,
    ChatAlreadyExists,
    SameUsersIds,
    FileNotFound,
    UserAlreadyInConversation,
    MessageNotFound,
    UserNotInConversation,
    FileRangeError,
    UnreadMessageAlreadyExists,
    generic_settings
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_schema()
    await create_tables()
    await setup_unread_messages_changes_trigger()
    await setup_recipients_change_trigger()
    await setup_user_delete_trigger()
    await setup_conversation_delete_trigger()
    await setup_messages_delete_trigger()
    asyncio.create_task(setup_unread_messages_changes_listener())
    asyncio.create_task(setup_recipients_change_listener())
    asyncio.create_task(setup_user_delete_listener())
    asyncio.create_task(setup_conversation_delete_listener())
    asyncio.create_task(setup_messages_delete_listener())

    FileManager.create_folders_structure()
    yield

app = FastAPI(
    title="ChatWave",
    description="ChatWave - Modern, Simple and Secure REST API for self-hosted messanger",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=generic_settings.API_CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(ConversationNotFoundError)
async def conversation_not_found_handler(request: Request, exc: ConversationNotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(AccessDeniedError)
async def access_denied_handler(request: Request, exc: AccessDeniedError):
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})


@app.exception_handler(IsNotAGroupError)
async def not_a_group_handler(request: Request, exc: IsNotAGroupError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(IsNotAChatError)
async def not_a_chat_handler(request: Request, exc: IsNotAChatError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(InvalidPasswordError)
async def invalid_password_handler(request: Request, exc: InvalidPasswordError):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentials)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.exception_handler(UserAlreadyExists)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(InvalidFileType)
async def invalid_file_type_handler(request: Request, exc: InvalidFileType):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(FIleToBig)
async def file_too_big_handler(request: Request, exc: FIleToBig):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(ImageCorrupted)
async def image_corrupted_handler(request: Request, exc: ImageCorrupted):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(ChatAlreadyExists)
async def chat_already_exists_handler(request: Request, exc: ChatAlreadyExists):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(SameUsersIds)
async def same_user_ids_handler(request: Request, exc: SameUsersIds):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(FileNotFound)
async def file_not_found_handler(request: Request, exc: FileNotFound):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyInConversation)
async def user_already_in_conversation_handler(request: Request, exc: UserAlreadyInConversation):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.exception_handler(MessageNotFound)
async def message_not_found_handler(request: Request, exc: MessageNotFound):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(UserNotInConversation)
async def user_not_in_conversation_handler(request: Request, exc: UserNotInConversation):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(FileRangeError)
async def file_range_error_handler(request: Request, exc: FileRangeError):
    return JSONResponse(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, content={"detail": str(exc)})


@app.exception_handler(UnreadMessageAlreadyExists)
async def unread_message_already_exists_handler(request: Request, exc: UnreadMessageAlreadyExists):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


app.include_router(authorization_router)

app.include_router(anonymous_users_router)
app.include_router(users_router)

app.include_router(conversations_router)

app.include_router(messages_router)
