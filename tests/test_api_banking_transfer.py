import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL, get_test_client


async def get_seeded_user_with_funds(client: httpx.AsyncClient):
    """Helper to find a seeded user with funds for transfer tests."""
    for i in range(1, 6):
        email = f"user{i}@example.com"
        res = await client.post(
            "/auth/login", json={"email": email, "password": "password123"}
        )
        if res.status_code == 200:
            token = res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            balance_res = await client.get("/banking/account/balance", headers=headers)
            if balance_res.json()["balance"] > 0:
                return token, email, balance_res.json()["balance"], headers
    return None, None, 0, None


@pytest.mark.asyncio
async def test_transfer_success():
    async with get_test_client() as client:
        # 1. Get a sender with funds
        (
            sender_token,
            sender_email,
            balance,
            sender_headers,
        ) = await get_seeded_user_with_funds(client)
        assert sender_token is not None, "Need a seeded user with funds"

        # 2. Get a recipient account ID
        res = await client.get("/banking/accounts", headers=sender_headers)
        accounts = res.json()
        recipient_id = accounts[0]["id"]

        # 3. Perform a small transfer
        transfer_amount = 100
        payload = {"recipient_id": recipient_id, "amount": transfer_amount}

        res = await client.post(
            "/banking/transfer", json=payload, headers=sender_headers
        )
        assert res.status_code in [200, 201]  # Normally 200 based on standard FastAPI

        data = res.json()
        assert data["amount"] == transfer_amount
        assert data["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_transfer_insufficient_funds():
    email = f"broke_{uuid4().hex[:8]}@example.com"
    password = "Password123!"

    async with get_test_client() as client:
        # Register a new user (balance 0)
        await client.post("/auth/register", json={"email": email, "password": password})
        login_res = await client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get a recipient account ID
        res = await client.get("/banking/accounts", headers=headers)
        recipient_id = res.json()[0]["id"]

        # Try to transfer
        payload = {"recipient_id": recipient_id, "amount": 1000}
        res = await client.post("/banking/transfer", json=payload, headers=headers)

        assert res.status_code == 402
        assert "Insufficient funds" in res.json()["detail"]


@pytest.mark.asyncio
async def test_transfer_to_self():
    async with get_test_client() as client:
        # We need the user's own account ID. Since /accounts excludes it, we must fetch it from another user's perspective.
        (
            sender_token,
            sender_email,
            balance,
            sender_headers,
        ) = await get_seeded_user_with_funds(client)

        # Log in as a different user to find the sender's account ID
        other_email = (
            "user2@example.com"
            if sender_email != "user2@example.com"
            else "user3@example.com"
        )
        res = await client.post(
            "/auth/login", json={"email": other_email, "password": "password123"}
        )
        other_token = res.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        res = await client.get("/banking/accounts", headers=other_headers)
        accounts = res.json()

        sender_account_id = None
        for acc in accounts:
            if sender_email in acc["display_name"]:
                sender_account_id = acc["id"]
                break

        assert sender_account_id is not None

        # Try to send to self
        payload = {"recipient_id": sender_account_id, "amount": 100}
        res = await client.post(
            "/banking/transfer", json=payload, headers=sender_headers
        )

        assert res.status_code == 422
        assert "Cannot transfer to self" in res.json()["detail"]


@pytest.mark.asyncio
async def test_transfer_nonexistent_recipient():
    async with get_test_client() as client:
        sender_token, _, _, sender_headers = await get_seeded_user_with_funds(client)
        fake_uuid = str(uuid4())

        payload = {"recipient_id": fake_uuid, "amount": 100}
        res = await client.post(
            "/banking/transfer", json=payload, headers=sender_headers
        )

        assert res.status_code == 404
        assert "Recipient not found" in res.json()["detail"]


@pytest.mark.asyncio
async def test_transfer_zero_or_negative_amount():
    async with get_test_client() as client:
        sender_token, _, _, sender_headers = await get_seeded_user_with_funds(client)

        # Get recipient
        res = await client.get("/banking/accounts", headers=sender_headers)
        recipient_id = res.json()[0]["id"]

        # Try amount 0
        payload = {"recipient_id": recipient_id, "amount": 0}
        res = await client.post(
            "/banking/transfer", json=payload, headers=sender_headers
        )
        assert res.status_code == 422  # Pydantic validation error

        # Try amount -100
        payload = {"recipient_id": recipient_id, "amount": -100}
        res = await client.post(
            "/banking/transfer", json=payload, headers=sender_headers
        )
        assert res.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_transfer_unauthenticated():
    async with get_test_client() as client:
        payload = {"recipient_id": str(uuid4()), "amount": 100}
        res = await client.post("/banking/transfer", json=payload)
        assert res.status_code == 401
