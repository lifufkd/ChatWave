from io import BytesIO
from pathlib import Path

from .base import BaseStorage
from utilities import generic_settings, InvalidFileType, FIleToBig, ImageCorrupted, MessagesTypes
from .utils import StorageUtils


class FileManager(BaseStorage):
    def __init__(self):
        pass

    @staticmethod
    def create_folders_structure():
        users_avatar_folder = generic_settings.MEDIA_FOLDER / "users" / "avatars"
        groups_avatar_folder = generic_settings.MEDIA_FOLDER / "groups" / "avatars"
        media_messages_folder = generic_settings.MEDIA_FOLDER / "messages" / "media"
        for folder in [users_avatar_folder, groups_avatar_folder, media_messages_folder]:
            StorageUtils.create_directory(path=folder)

    async def file_exists(self, file_path: Path) -> bool:
        return await StorageUtils.file_exists(file_path=file_path)

    async def write_file(self, file_path: Path, file_data: bytes) -> None:
        await StorageUtils.write_file(file_path=file_path, file_data=file_data)

    async def read_file(self, file_path: Path) -> bytes:
        return await StorageUtils.read_file(file_path=file_path)

    async def delete_file(self, file_path: Path) -> None:
        await StorageUtils.delete_file(file_path=file_path)

    async def archive_files(self, files_paths: list[Path]) -> BytesIO:
        return await StorageUtils().archive_files(files_paths=files_paths)

    async def validate_file(
            self,
            file_content: bytes,
            file_type: str,
            file_type_filter
    ) -> None:
        await StorageUtils().validate_file(
            file_content=file_content,
            file_type=file_type,
            file_type_filter=file_type_filter
        )

    async def detect_file_type(self, file_type: str) -> MessagesTypes:
        return await StorageUtils().detect_file_type(file_type=file_type)


