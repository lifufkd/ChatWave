import pytest
import pathlib
import io
from contextlib import nullcontext as does_not_raise

from fixtures.storage_fixtures import create_storage_instance, garbage_cleaner
from utilities import MediaPatches, MessagesTypes, ImageCorrupted, FIleToBig


async def test_create_folders_structure(create_storage_instance):
    create_storage_instance.create_folders_structure()

    assert pathlib.Path(MediaPatches.USERS_AVATARS_FOLDER.value).is_dir()
    assert pathlib.Path(MediaPatches.GROUPS_AVATARS_FOLDER.value).is_dir()
    assert pathlib.Path(MediaPatches.MEDIA_MESSAGES_FOLDER.value).is_dir()


@pytest.mark.parametrize(
    "path, expected",
    [
        ("tests/media/users_avatars/valid.jpg", True),
        ("/", False)
    ]
)
async def test_file_exists(create_storage_instance, path, expected):
    if await create_storage_instance.file_exists(pathlib.Path(path)) == expected:
        assert True


@pytest.mark.dependency(name="test_write_file")
@pytest.mark.parametrize(
    "path",
    [
        (MediaPatches.USERS_AVATARS_FOLDER.value / "test_image.jpg", ),
        (MediaPatches.GROUPS_AVATARS_FOLDER.value / "test_image.jpg", ),
        (MediaPatches.MEDIA_MESSAGES_FOLDER.value / "test_image.jpg", ),
    ]
)
async def test_write_file(create_storage_instance, garbage_cleaner, path):
    await create_storage_instance.write_file(
        file_path=pathlib.Path(path[0]),
        file_data=io.FileIO("tests/media/users_avatars/valid.jpg", 'rb').read()
    )


@pytest.mark.dependency(depends=["test_write_file"])
async def test_read_file(create_storage_instance, garbage_cleaner):
    await create_storage_instance.write_file(
        file_path=pathlib.Path(MediaPatches.USERS_AVATARS_FOLDER.value / "test_image.jpg"),
        file_data=io.FileIO("tests/media/users_avatars/valid.jpg", 'rb').read()
    )

    assert await create_storage_instance.read_file(
        file_path=pathlib.Path(MediaPatches.USERS_AVATARS_FOLDER.value / "test_image.jpg")
    )


@pytest.mark.dependency(depends=["test_write_file"])
async def test_delete_file(create_storage_instance):
    await create_storage_instance.write_file(
        file_path=pathlib.Path(MediaPatches.USERS_AVATARS_FOLDER.value / "test_image.jpg"),
        file_data=io.FileIO("tests/media/users_avatars/valid.jpg", 'rb').read()
    )

    await create_storage_instance.delete_file(
        file_path=pathlib.Path(MediaPatches.USERS_AVATARS_FOLDER.value / "test_image.jpg")
    )


async def test_check_file_size(create_storage_instance):
    assert await create_storage_instance.check_file_size(file_path=pathlib.Path("tests/media/users_avatars/valid.jpg"))


async def test_archive_files(create_storage_instance):
    assert await create_storage_instance.archive_files(
        files_paths=[
            pathlib.Path("tests/media/users_avatars/valid.jpg"),
            pathlib.Path("tests/media/users_avatars/invalid.jpg")
        ]
    )


async def test_file_chunk_generator(create_storage_instance):
    assert await create_storage_instance.file_chunk_generator(
        file_paths=[
            pathlib.Path("tests/media/users_avatars/valid.jpg"),
            pathlib.Path("tests/media/users_avatars/invalid.jpg")
        ]
    )


@pytest.mark.parametrize(
    "file_content, file_type, file_type_filter, exception",
    [
        ("tests/media/users_avatars/valid.jpg", "image/jpeg", MessagesTypes.IMAGE, does_not_raise()),
        ("tests/media/users_avatars/invalid.jpg", "image/jpeg", MessagesTypes.IMAGE, pytest.raises(ImageCorrupted)),
        ("tests/media/users_avatars/oversized.jpg", "image/jpeg", MessagesTypes.IMAGE, pytest.raises(FIleToBig)),
        ("tests/media/users_avatars/text.txt", "text/plain", MessagesTypes.FILE, does_not_raise()),
    ]
)
async def test_validate_file(create_storage_instance, file_content, file_type, file_type_filter, exception):
    with exception:
        await create_storage_instance.validate_file(
            file_content=pathlib.Path(file_content).read_bytes(),
            file_type=file_type,
            file_type_filter=file_type_filter
        )


@pytest.mark.parametrize(
    "file_type, expected",
    [
        ("image/jpeg", MessagesTypes.IMAGE),
        ("image/jpg", MessagesTypes.FILE),
        ("video/mp4", MessagesTypes.VIDEO),
        ("audio/mp4ex", MessagesTypes.FILE),
        ("audio/mpeg", MessagesTypes.AUDIO),
        ("audio/mpeg33", MessagesTypes.FILE),
        ("text/plain", MessagesTypes.FILE),
    ]
)
async def test_detect_file_type(create_storage_instance, file_type, expected):
    assert await create_storage_instance.detect_file_type(file_type=file_type) == expected
