import asyncio

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from contextlib import asynccontextmanager

from dependencies import redis_client
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
from repository import create_tables
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
    UnreadMessageAlreadyExists
)


@asynccontextmanager
async def lifespan(_: FastAPI):
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
    FastAPICache.init(RedisBackend(redis_client), prefix="chatwave-cache")
    yield

app = FastAPI(
    title="ChatWave",
    description="ChatWave - Modern, Simple and Secure REST API for self-hosted messanger",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def exception_handler(request, exc: Exception) -> JSONResponse:
    match exc:
        case UserNotFoundError():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(exc)}
            )
        case ConversationNotFoundError():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(exc)}
            )
        case AccessDeniedError():
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": str(exc)}
            )
        case IsNotAGroupError():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)}
            )
        case IsNotAChatError():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)}
            )
        case InvalidPasswordError():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(exc)}
            )
        case InvalidCredentials():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(exc)},
                headers={"WWW-Authenticate": "Bearer"}
            )
        case UserAlreadyExists():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": str(exc)},
            )
        case InvalidFileType():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )
        case FIleToBig():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )
        case ImageCorrupted():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )
        case ChatAlreadyExists():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": str(exc)}
            )
        case SameUsersIds():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)}
            )
        case FileNotFound():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(exc)}
            )
        case UserAlreadyInConversation():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": str(exc)}
            )
        case MessageNotFound():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(exc)}
            )
        case UserNotInConversation():
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(exc)}
            )
        case FileRangeError():
            return JSONResponse(
                status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                content={"detail": str(exc)}
            )
        case UnreadMessageAlreadyExists():
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": str(exc)}
            )


app.include_router(authorization_router)

app.include_router(anonymous_users_router)
app.include_router(users_router)

app.include_router(conversations_router)

app.include_router(messages_router)

