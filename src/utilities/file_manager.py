import sys
import io
import zipfile
from pathlib import Path
from PIL import Image
from typing import Union

from utilities import generic_settings, InvalidFileType, FIleToBig, ImageCorrupted, MessagesTypes


class FileManager:
    def __init__(self):
        pass

    def init_folders(self):
        media_folder = generic_settings.MEDIA_FOLDER
        avatars_folder = media_folder / "avatars"
        messages_folder = media_folder / "messages"
        groups_folder = media_folder / "groups" / "avatars"
        for folder in [avatars_folder, messages_folder, groups_folder]:
            self.create_directory(folder)

    @staticmethod
    def create_directory(path: Path):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            sys.exit(f"Error creating directory {path}: {e}")

    @staticmethod
    def write_file(path: Path, content: bytes):
        with open(str(path), "wb") as f:
            f.write(content)

    @staticmethod
    def read_file(path: Path):
        with open(str(path), "rb") as f:
            return f.read()

    @staticmethod
    def file_exists(path: Path) -> bool:
        return path.exists() and path.is_file()

    @staticmethod
    def delete_file(path: Path) -> None:
        path.unlink()

    def archive_files(self, paths: list[Path]) -> io.BytesIO:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in paths:
                if self.file_exists(file_path):
                    zip_file.write(file_path, arcname=file_path.name)

        zip_buffer.seek(0)

        return zip_buffer

    @staticmethod
    def calculate_file_size(file: bytes) -> float:
        file_size_mb = len(file) / (1024 * 1024)
        return file_size_mb

    @staticmethod
    def validate_file_size(
            file_size: float,
            max_allowed_file_size: Union[
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
    def validate_file_integrity(
            file: bytes,
            file_type: Union[
                MessagesTypes.IMAGE,
                MessagesTypes.VIDEO,
                MessagesTypes.AUDIO,
                MessagesTypes.FILE
            ]
    ) -> bool:
        match file_type:
            case MessagesTypes.IMAGE:
                try:
                    image = Image.open(file)
                    image.verify()
                except:
                    return False
            case MessagesTypes.VIDEO:
                pass
            case MessagesTypes.AUDIO:
                pass
            case MessagesTypes.FILE:
                pass

        return True

    @staticmethod
    def validate_file_type(
            file_type: str | None,
            allowed_file_type
    ) -> bool:
        if file_type not in allowed_file_type:
            return False

        return True

    def validate_file(
            self,
            file_content: bytes,
            file_type: str,
            file_type_filter
    ) -> None:

        def get_allowed_types() -> list:
            match file_type_filter:
                case MessagesTypes.IMAGE:
                    return generic_settings.ALLOWED_IMAGE_TYPES
                case MessagesTypes.VIDEO:
                    return generic_settings.ALLOWED_VIDEO_TYPES
                case MessagesTypes.AUDIO:
                    return generic_settings.ALLOWED_AUDIO_TYPES
                case MessagesTypes.FILE:
                    return list()

        def get_max_upload_size() -> int:
            match file_type_filter:
                case MessagesTypes.IMAGE:
                    return generic_settings.MAX_UPLOAD_IMAGE_SIZE
                case MessagesTypes.VIDEO:
                    return generic_settings.MAX_UPLOAD_VIDEO_SIZE
                case MessagesTypes.AUDIO:
                    return generic_settings.MAX_UPLOAD_AUDIO_SIZE
                case MessagesTypes.FILE:
                    return generic_settings.MAX_UPLOAD_FILE_SIZE

        def get_integrity_exception() -> Exception:
            match file_type_filter:
                case MessagesTypes.IMAGE:
                    return ImageCorrupted(detail="Image file is corrupted")
                case MessagesTypes.VIDEO:
                    pass
                case MessagesTypes.AUDIO:
                    pass
                case MessagesTypes.FILE:
                    pass

        actual_file_type = self.detect_file_type(file_type=file_type)
        if actual_file_type != file_type_filter:
            raise InvalidFileType(
                detail=f"Invalid {file_type_filter} type. Only {', '.join(get_allowed_types())} are allowed.")

        file_size_mb = self.calculate_file_size(file=file_content)
        if not self.validate_file_size(file_size=file_size_mb,
                                       max_allowed_file_size=get_max_upload_size()):
            raise FIleToBig(detail=f"{file_type_filter} size exceeds {get_max_upload_size()} MB limit.")

        if not self.validate_file_integrity(file=file_content,file_type=file_type):
            raise get_integrity_exception()

    def detect_file_type(self, file_type: str) -> MessagesTypes:

        if self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_IMAGE_TYPES):
            return MessagesTypes.IMAGE
        elif self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_VIDEO_TYPES):
            return MessagesTypes.VIDEO
        elif self.validate_file_type(file_type=file_type, allowed_file_type=generic_settings.ALLOWED_AUDIO_TYPES):
            return MessagesTypes.AUDIO
        else:
            return MessagesTypes.FILE


