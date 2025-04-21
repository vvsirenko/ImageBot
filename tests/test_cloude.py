from unittest.mock import MagicMock, patch

import fastapi
import pytest

from storage.client import S3Client


@pytest.fixture
def s3_client():
    return S3Client(cloud_token="fake_token")


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1234
    return user


async def test_upload_zip_file_not_found(s3_client, mock_user):
    cloud_url = "https://fake-cloud.com/upload_zip"
    mock_file = MagicMock()
    mock_file.name = "nonexistent.zip"

    with patch("builtins.open", side_effect=FileNotFoundError()):
        with pytest.raises(fastapi.HTTPException):
            await s3_client.upload_zip(mock_file, cloud_url, mock_user)


async def test_upload_zip_unexpected_error(s3_client, mock_user):
    cloud_url = "https://fake-cloud.com/upload_zip"
    mock_file = MagicMock()
    mock_file.name = "test.zip"

    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        with pytest.raises(fastapi.HTTPException):
            await s3_client.upload_zip(mock_file, cloud_url, mock_user)

