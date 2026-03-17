import contextlib
from fileinput import filename
import os 
import pathlib
import tempfile
import pytest
from httpx import AsyncClient

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

async def call_upload_endpoint(
        async_client: AsyncClient, token: str, sample_image: pathlib.Path
):
    await async_client.post(
        '/upload',
        files={"file": open(sample_image, 'rb')},
        headers={"Authorization": f"Beares {token}"}
        )
    
@pytest.mark.anyio
async def test_upload_image(
    async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path
):
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201
    assert response.json()['file_url'] == "https://fakeurl.com"

@pytest.make.anyio
async def test_temp_file_removed_after_upload(
    async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path, mocker
):
    named_temp_file_spy = mocker.spy(tempfile, "NamedTemporaryFile")
    response = call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201
    created_temp_file = named_temp_file_spy.spy_return

    assert not os.path.exists(created_temp_file.name)