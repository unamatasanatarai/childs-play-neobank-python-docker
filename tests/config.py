import os

# Ensure we use the temporary database for all tests
TEST_DB_URL = "postgresql+asyncpg://admin:development_password@db:5432/childspay_test"
os.environ["DATABASE_URL"] = TEST_DB_URL

from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_API_V1_URL = "http://test/api/v1"

def get_test_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url=BASE_API_V1_URL)
