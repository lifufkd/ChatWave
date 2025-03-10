import zipfile
from PIL import Image
from typing import Union, Literal
from pathlib import Path
from io import BytesIO

from utilities import generic_settings, MessagesTypes, ImageCorrupted, InvalidFileType, FIleToBig


class StorageUtils:
    def __init__(self):
        pass

    @staticmethod
    def create_directory(path: Path):
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    async def write_file(file_path: Path, file_data: bytes):
        with open(str(file_path), "wb") as f:
            f.write(file_data)

    @staticmethod
    async def read_file(file_path: Path):
        with open(str(file_path), "rb") as f:
            return f.read()

    @staticmethod
    async def delete_file(file_path: Path) -> None:
        file_path.unlink()

    @staticmethod
    async def file_exists(file_path: Path) -> bool:
        return file_path.exists() and file_path.is_file()

    @staticmethod
    async def check_file_size(file_path: Path) -> int:
        return file_path.stat().st_size

    async def archive_files(self, files_paths: list[Path]) -> BytesIO:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in files_paths:
                if await self.file_exists(file_path=file_path):
                    zip_file.write(file_path, arcname=file_path.name)

        zip_buffer.seek(0)
        return zip_buffer

    @staticmethod
    async def file_chunk_generator(file_paths: list[Path]):
        for file_path in file_paths:
            with open(file_path, "rb") as f:
                while chunk := f.read(generic_settings.CHUNK_SIZE):
                    yield chunk

    @staticmethod
    async def range_file_chunk_generator(file_path: Path, start_byte: int, end_byte: int):
        with open(file_path, "rb") as f:
            f.seek(start_byte)
            yield f.read(end_byte - start_byte + 1)

    @staticmethod
    async def calculate_file_size(file: bytes) -> float:
        file_size_mb = len(file) / (1024 * 1024)
        return file_size_mb

    @staticmethod
    async def validate_file_size(
            file_size: float,
            max_allowed_file_size:
            Union[
                generic_settings.MAX_UPLOAD_IMAGE_SIZE,
                generic_settings.MAX_UPLOAD_VIDEO_SIZE,
                generic_settings.MAX_UPLOAD_AUDIO_SIZE,
                generic_settings.MAX_UPLOAD_FILE_SIZE
            ]
    ) -> bool:
        if file_size > max_allowed_file_size:
            return False

        return True

    @staticmethod
    async def validate_file_integrity(
            file: bytes,
            file_type:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ]
    ) -> bool:
        match file_type:
            case MessagesTypes.IMAGE:
                try:
                    image = Image.open(BytesIO(file))
                    image.verify()
                except Exception as e:
                    print(e)
                    return False
            case MessagesTypes.VIDEO:
                pass
            case MessagesTypes.AUDIO:
                pass
            case MessagesTypes.FILE:
                pass

        return True

    @staticmethod
    async def validate_file_type(
            file_type: str | None,
            allowed_file_type
    ) -> bool:
        if file_type not in allowed_file_type:
            return False

        return True

    @staticmethod
    async def _get_allowed_types(
            file_type_filter:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ]) -> list:
        match file_type_filter:
            case MessagesTypes.IMAGE:
                return generic_settings.ALLOWED_IMAGE_TYPES
            case MessagesTypes.VIDEO:
                return generic_settings.ALLOWED_VIDEO_TYPES
            case MessagesTypes.AUDIO:
                return generic_settings.ALLOWED_AUDIO_TYPES
            case MessagesTypes.FILE:
                return list()

    @staticmethod
    async def _get_max_upload_size(
            file_type_filter:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ]) -> int:
        match file_type_filter:
            case MessagesTypes.IMAGE:
                return generic_settings.MAX_UPLOAD_IMAGE_SIZE
            case MessagesTypes.VIDEO:
                return generic_settings.MAX_UPLOAD_VIDEO_SIZE
            case MessagesTypes.AUDIO:
                return generic_settings.MAX_UPLOAD_AUDIO_SIZE
            case MessagesTypes.FILE:
                return generic_settings.MAX_UPLOAD_FILE_SIZE

    @staticmethod
    async def _get_integrity_exception(
            file_type_filter:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ]) -> Exception:
        match file_type_filter:
            case MessagesTypes.IMAGE:
                return ImageCorrupted()
            case MessagesTypes.VIDEO:
                pass
            case MessagesTypes.AUDIO:
                pass
            case MessagesTypes.FILE:
                pass

    async def validate_file(
            self,
            file_content: bytes,
            file_type: str,
            file_type_filter:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ]
    ) -> None:

        actual_file_type = await self.detect_file_type(file_type=file_type)
        if actual_file_type != file_type_filter:
            raise InvalidFileType(
                file_type_name=file_type_filter.value,
                file_types=', '.join(await self._get_allowed_types(file_type_filter))
            )

        file_size_mb = await self.calculate_file_size(file=file_content)
        if not await self.validate_file_size(file_size=file_size_mb,
                                             max_allowed_file_size=await self._get_max_upload_size(file_type_filter)):
            raise FIleToBig(
                file_type_name=file_type_filter.value,
                size_limit=await self._get_max_upload_size(file_type_filter)
            )

        if not (await self.validate_file_integrity(file=file_content, file_type=actual_file_type)):
            raise await self._get_integrity_exception(file_type_filter)

    async def detect_file_type(
            self,
            file_type: str)\
            -> Union[Literal[MessagesTypes.IMAGE, MessagesTypes.VIDEO, MessagesTypes.AUDIO, MessagesTypes.FILE]]:

        if await self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_IMAGE_TYPES):
            return MessagesTypes.IMAGE
        elif await self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_VIDEO_TYPES):
            return MessagesTypes.VIDEO
        elif await self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_AUDIO_TYPES):
            return MessagesTypes.AUDIO
        else:
            return MessagesTypes.FILE
