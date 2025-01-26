from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path

from utilities import MessagesTypes


class BaseStorage(ABC):

    @abstractmethod
    async def file_exists(self, file_path: Path) -> bool:
        pass

    @abstractmethod
    async def write_file(self, file_path: Path, file_data: bytes) -> None:
        pass

    @abstractmethod
    async def read_file(self, file_path: Path) -> None:
        pass

    @abstractmethod
    async def delete_file(self, file_path: Path) -> None:
        pass

    @abstractmethod
    async def archive_files(self, files_paths: list[Path]) -> BytesIO:
        pass

    @abstractmethod
    async def validate_file(
            self,
            file_content: bytes,
            file_type: str,
            file_type_filter
    ) -> None:
        pass

    @abstractmethod
    async def detect_file_type(self, file_type: str) -> MessagesTypes:
        pass
