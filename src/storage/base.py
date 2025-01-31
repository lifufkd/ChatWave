from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Iterator

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
    async def file_chunk_generator(self, file_paths: list[Path]):
        pass

    @abstractmethod
    async def check_file_size(self, file_path: Path) -> int:
        pass

    @abstractmethod
    async def range_file_chunk_generator(self, file_path: Path, start_byte: int, end_byte: int):
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
