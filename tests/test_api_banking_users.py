import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL, get_test_client


@pytest.mark.asyncio
async def test_list_users_success_and_exclusion():
    email = f"users_{uuid4().hex[:8]}@example.com"
    password = "Password123!"

    async with get_test_client() as client:
        # Register and Login
        await client.post("/auth/register", json={"email": email, "password": password})
        login_res = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get users
        res = await client.get("/banking/users", headers=headers)
        assert res.status_code == 200
        users = res.json()

        assert isinstance(users, list)
        # Ensure the current user is NOT in the list
        for u in users:
            assert u["email"] != email
            assert "id" in u


@pytest.mark.asyncio
async def test_list_users_unauthenticated():
    async with get_test_client() as client:
        res = await client.get("/banking/users")
        assert res.status_code == 401
        assert "Not authenticated" in res.json()["detail"]


@pytest.mark.asyncio
async def test_list_users_invalid_token():
    headers = {"Authorization": "Bearer invalid.token.here"}
    async with get_test_client() as client:
        res = await client.get("/banking/users", headers=headers)
        assert res.status_code == 401
