import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi import status, FastAPI
from fastapi.testclient import TestClient
from storage.client import S3ClientABC
from io import BytesIO
from rest_api.routes import router as telegram_router


app = FastAPI()
app.include_router(telegram_router)


client = TestClient(app)


@pytest.fixture
def fake_zip_file():
    """Create a fake zip file for testing."""
    file = BytesIO(b"Fake zip content")
    file.name = "test.zip"
    return file


@pytest.fixture
def fake_user():
    """Return a fake user JSON string."""
    return json.dumps({"id": "123465", "first_name": "test_user"})


@pytest.fixture
def mock_s3_client():
    """Mock the S3ClientABC dependency."""
    mock = AsyncMock(spec=S3ClientABC)
    mock.service_name = "mock_s3"
    return mock


async def test_upload_zip_success(fake_zip_file, fake_user):
    with patch("rest_api.routes.upload_zip_utils", new_callable=AsyncMock) as mock_upload_zip:
        mock_upload_zip.return_value = {"success": True}
        response = client.post(
            "/upload_zip/",
            files={"file": ("test.zip", fake_zip_file, "application/zip")},
            data={"user": fake_user},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['status_code'] == 201
        assert response.json()["body"]["response"] == {'success': True}

