import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL, get_test_client


@pytest.mark.asyncio
async def test_get_balance_success():
    email = f"balance_{uuid4().hex[:8]}@example.com"
    password = "Password123!"

    async with get_test_client() as client:
        # Register and Login
        await client.post("/auth/register", json={"email": email, "password": password})
        login_res = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get balance
        res = await client.get("/banking/account/balance", headers=headers)
        assert res.status_code == 200
        data = res.json()

        # New users start with 0 balance
        assert data["balance"] == 0
        assert "account_number" in data
        assert data["account_number"].startswith("CHPAY-")


@pytest.mark.asyncio
async def test_get_balance_unauthenticated():
    async with get_test_client() as client:
        res = await client.get("/banking/account/balance")
        assert res.status_code == 401
