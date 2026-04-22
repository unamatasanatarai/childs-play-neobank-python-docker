import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL, get_test_client


@pytest.mark.asyncio
async def test_login_success():
    email = f"login_user_{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"

    async with get_test_client() as client:
        # Register first
        await client.post("/auth/register", json={"email": email, "password": password})

        # Then login
        res = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password():
    email = f"login_wrong_{uuid4().hex[:8]}@example.com"

    async with get_test_client() as client:
        await client.post(
            "/auth/register", json={"email": email, "password": "CorrectPassword1!"}
        )

        res = await client.post(
            "/auth/login", json={"email": email, "password": "WrongPassword2@"}
        )
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]


@pytest.mark.asyncio
async def test_login_non_existent_user():
    email = f"nonexistent_{uuid4().hex[:8]}@example.com"

    async with get_test_client() as client:
        res = await client.post(
            "/auth/login", json={"email": email, "password": "SomePassword1!"}
        )
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]


@pytest.mark.asyncio
async def test_login_missing_fields():
    async with get_test_client() as client:
        res = await client.post("/auth/login", json={"email": "test@example.com"})
        assert res.status_code == 422
