import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL


@pytest.mark.asyncio
async def test_list_accounts_success():
    email = f"accounts_{uuid4().hex[:8]}@example.com"
    password = "Password123!"

    async with httpx.AsyncClient(base_url=BASE_API_V1_URL) as client:
        # Register and Login
        await client.post("/auth/register", json={"email": email, "password": password})
        login_res = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get accounts
        res = await client.get("/banking/accounts", headers=headers)
        assert res.status_code == 200
        accounts = res.json()

        assert isinstance(accounts, list)
        for acc in accounts:
            # Should contain display_name and id
            assert "id" in acc
            assert "display_name" in acc
            # Current user's email should NOT be in any display_name
            assert email not in acc["display_name"]


@pytest.mark.asyncio
async def test_list_accounts_unauthenticated():
    async with httpx.AsyncClient(base_url=BASE_API_V1_URL) as client:
        res = await client.get("/banking/accounts")
        assert res.status_code == 401
