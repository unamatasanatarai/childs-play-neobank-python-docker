import asyncio
import pytest
import httpx

from tests.config import BASE_API_V1_URL, get_test_client


@pytest.mark.asyncio
async def test_double_spend_prevention():
    """
    Test that sending two simultaneous requests for the FULL balance
    results in only one success and one 'Insufficient Funds' error.
    """
    # 1. Login as a User (seeded with 10,000)
    async with get_test_client() as client:
        sender_token = None
        balance = 0
        sender_email = ""
        for i in range(1, 6):
            email = f"user{i}@example.com"
            res = await client.post(
                "/auth/login", json={"email": email, "password": "password123"}
            )
            if res.status_code == 200:
                token = res.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                res = await client.get("/banking/account/balance", headers=headers)
                b = res.json()["balance"]
                if b > 0:
                    sender_token = token
                    balance = b
                    sender_email = email
                    break

        assert sender_token is not None, "No users found with a positive balance"
        headers = {"Authorization": f"Bearer {sender_token}"}

        # 3. Get a recipient's account ID
        res = await client.get("/banking/accounts", headers=headers)
        accounts = res.json()
        assert len(accounts) > 0, "No recipient accounts found"
        recipient_id = accounts[0]["id"]

        # 4. Trigger two concurrent requests trying to drain the full balance twice
        payload = {"recipient_id": recipient_id, "amount": balance}

        tasks = [
            client.post("/banking/transfer", json=payload, headers=headers),
            client.post("/banking/transfer", json=payload, headers=headers),
        ]

        responses = await asyncio.gather(*tasks)

    # 5. Analyze results
    status_codes = [r.status_code for r in responses]

    # We expect exactly one 200 (OK) and one 402 (Payment Required)
    if 200 not in status_codes:
        print("Responses:", [r.json() for r in responses])
    assert 200 in status_codes
    assert 402 in status_codes
    print("✅ Double-spend prevented successfully.")
