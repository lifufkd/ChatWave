import pytest
import os
import shutil

from storage import FileManager
from utilities import generic_settings


@pytest.fixture(scope='module')
async def create_storage_instance():
    file_manager_obj = FileManager()

    yield file_manager_obj

    del file_manager_obj


@pytest.fixture(scope='function')
async def garbage_cleaner():
    yield

    for root, dirs, files in os.walk(str(generic_settings.MEDIA_FOLDER),
                                     topdown=False):
        for d in dirs:
            if d.startswith("test_"):
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if f.startswith("test_"):
                os.remove(os.path.join(root, f))
