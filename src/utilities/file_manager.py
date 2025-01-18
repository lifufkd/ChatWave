import sys
import io
import zipfile
from fastapi import UploadFile
from pathlib import Path
from PIL import Image

from utilities import generic_settings, InvalidFileType, FIleToBig, ImageCorrupted


class FileManager:
    def __init__(self):
        pass

    def init_folders(self):
        media_folder = generic_settings.MEDIA_FOLDER
        avatars_folder = media_folder / "avatars"
        messages_folder = media_folder / "messages"
        groups_folder = media_folder / "groups" / "avatars"
        for folder in [avatars_folder, messages_folder, groups_folder]:
            self._create_directory(folder)

    @staticmethod
    def _create_directory(path: Path):
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

    def pack_to_zip_files(self, paths: list[Path]) -> io.BytesIO:
        zip_obj = self.archive_files(paths=paths)
        return zip_obj

    def archive_files(self, paths: list[Path]) -> io.BytesIO:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for avatar_path in paths:
                if self.file_exists(avatar_path):
                    zip_file.write(avatar_path, arcname=avatar_path.name)

        zip_buffer.seek(0)

        return zip_buffer

    @staticmethod
    def validate_image(file: UploadFile) -> None:

        if file.content_type not in generic_settings.ALLOWED_MEDIA_TYPES:
            raise InvalidFileType(detail=f"Invalid image type. Only {generic_settings.ALLOWED_MEDIA_TYPES} are allowed.")

        file_size_mb = len(file.file.read()) / (1024 * 1024)
        file.file.seek(0)
        if file_size_mb > generic_settings.MAX_UPLOAD_SIZE:
            raise FIleToBig(detail=f"File size exceeds {generic_settings.MAX_UPLOAD_SIZE} MB limit.")

        try:
            image = Image.open(file.file)
            image.verify()
            file.file.seek(0)
        except Exception:
            raise ImageCorrupted(detail="Invalid image file.")

