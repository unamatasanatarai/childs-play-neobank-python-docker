import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL, get_test_client


@pytest.mark.asyncio
async def test_register_success():
    email = f"user_{uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "StrongPassword123!"}

    async with get_test_client() as client:
        res = await client.post("/auth/register", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == email
        assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email():
    email = f"duplicate_{uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "StrongPassword123!"}

    async with get_test_client() as client:
        # First registration
        res1 = await client.post("/auth/register", json=payload)
        assert res1.status_code == 201

        # Second registration with same email
        res2 = await client.post("/auth/register", json=payload)
        assert res2.status_code == 400
        assert "Email already registered" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email_format():
    payload = {"email": "not-an-email", "password": "StrongPassword123!"}

    async with get_test_client() as client:
        res = await client.post("/auth/register", json=payload)
        assert res.status_code == 422
        assert "value is not a valid email address" in str(res.json()["detail"]).lower()


@pytest.mark.asyncio
async def test_register_missing_fields():
    async with get_test_client() as client:
        res = await client.post("/auth/register", json={"email": "test@example.com"})
        assert res.status_code == 422

        res = await client.post("/auth/register", json={"password": "password123"})
        assert res.status_code == 422
