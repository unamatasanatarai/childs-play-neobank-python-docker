import pytest
import httpx
from uuid import uuid4

from tests.config import BASE_API_V1_URL

@pytest.mark.asyncio
async def test_end_to_end_user_journey():
    """
    Simulates a full user journey:
    1. A new user registers.
    2. A seeded user (with funds) logs in.
    3. The seeded user transfers money to the new user.
    4. The new user logs in and verifies their new balance.
    5. The new user attempts to over-transfer (fails).
    6. The new user successfully transfers a partial amount back.
    7. Both balances are verified at the end.
    """
    new_user_email = f"e2e_user_{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"

    async with httpx.AsyncClient(base_url=BASE_API_V1_URL) as client:
        # Step 1: Register new user
        res = await client.post("/auth/register", json={"email": new_user_email, "password": password})
        assert res.status_code == 201

        # Step 2: Seeded user logs in
        seeded_token = None
        seeded_user_email = ""
        seeded_initial_balance = 0
        for i in range(1, 6):
            email = f"user{i}@example.com"
            res = await client.post("/auth/login", json={"email": email, "password": "password123"})
            if res.status_code == 200:
                token = res.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                res = await client.get("/banking/account/balance", headers=headers)
                b = res.json()["balance"]
                if b > 0:
                    seeded_token = token
                    seeded_initial_balance = b
                    seeded_user_email = email
                    break

        assert seeded_token is not None, "Seeded user must have funds for E2E test"
        seeded_headers = {"Authorization": f"Bearer {seeded_token}"}

        # Step 3: Seeded user finds new user's account ID
        res = await client.get("/banking/accounts", headers=seeded_headers)
        assert res.status_code == 200
        accounts = res.json()
        new_user_account = next((acc for acc in accounts if new_user_email in acc["display_name"]), None)
        assert new_user_account is not None, "New user account not found in accounts list"
        new_user_account_id = new_user_account["id"]

        # Step 4: Seeded user transfers 5000 cents ($50.00) to new user
        transfer_amount = 5000
        res = await client.post(
            "/banking/transfer", 
            json={"recipient_id": new_user_account_id, "amount": transfer_amount}, 
            headers=seeded_headers
        )
        assert res.status_code in [200, 201]

        # Verify seeded user's new balance
        res = await client.get("/banking/account/balance", headers=seeded_headers)
        assert res.json()["balance"] == seeded_initial_balance - transfer_amount

        # Step 5: New user logs in
        res = await client.post("/auth/login", json={"email": new_user_email, "password": password})
        assert res.status_code == 200
        new_user_token = res.json()["access_token"]
        new_user_headers = {"Authorization": f"Bearer {new_user_token}"}

        # New user checks balance (should be 5000)
        res = await client.get("/banking/account/balance", headers=new_user_headers)
        assert res.status_code == 200
        assert res.json()["balance"] == transfer_amount

        # Step 6: New user attempts to transfer 6000 cents (should fail)
        # Find seeded user's account ID from new user's perspective
        res = await client.get("/banking/accounts", headers=new_user_headers)
        accounts = res.json()
        seeded_user_account = next((acc for acc in accounts if seeded_user_email in acc["display_name"]), None)
        assert seeded_user_account is not None
        seeded_user_account_id = seeded_user_account["id"]

        res = await client.post(
            "/banking/transfer", 
            json={"recipient_id": seeded_user_account_id, "amount": 6000}, 
            headers=new_user_headers
        )
        assert res.status_code == 402
        assert "Insufficient funds" in res.json()["detail"]

        # Step 7: New user successfully transfers 2500 cents back
        res = await client.post(
            "/banking/transfer", 
            json={"recipient_id": seeded_user_account_id, "amount": 2500}, 
            headers=new_user_headers
        )
        assert res.status_code in [200, 201]

        # Step 8: Final balance verifications
        res = await client.get("/banking/account/balance", headers=new_user_headers)
        assert res.json()["balance"] == transfer_amount - 2500  # 2500 remaining

        res = await client.get("/banking/account/balance", headers=seeded_headers)
        assert res.json()["balance"] == seeded_initial_balance - transfer_amount + 2500
