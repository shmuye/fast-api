import contextlib
import pathlib
from fileinput import filename

import pytest


@pytest.fixture()
def sample_image(fs) -> pathlib.path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path

@pytest.fixture(autouse=True)
def mock_b2_upload_file(mocker):
    return mocker.patch(
        "api.routers.upload.b2_upload_file", return_value="https://fakeurl.com"
    )

@pytest.fixture(autouse=True)
def aiofiles_mock_open(mocker, fs):
    mock_open = mocker.patch("aiofiles.open")
    @contextlib.asynccontextmanager
    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.asyncMock(name=f"async_file_open: {filename!r}/{mode!r}")
        with open(filename, mode) as fin:
            out_fs_mock.write_side_effect = fin.read
            out_fs_mock.write_side_effect = fin.write
            yield out_fs_mock

        mock_open.side_effect = async_file_open
        return mock_open