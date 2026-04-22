import asyncio
import pytest
import httpx
from uuid import uuid4

# Assuming the server is running via 'make up'
BASE_URL = "http://localhost:8000/api/v1"


@pytest.mark.asyncio
async def test_double_spend_prevention():
    """
    Test that sending two simultaneous requests for the same balance
    results in only one success and one 'Insufficient Funds' error.
    """
    # 1. Setup: Seed two temporary users via the API or use seeded accounts
    # Let's assume user1 has 1000 units and wants to send 1000 units twice.
    sender_token = "SENDER_JWT_HERE"  # In practice, login and get this
    recipient_id = str(uuid4())  # A random valid recipient ID

    payload = {"recipient_id": recipient_id, "amount": 1000}
    headers = {"Authorization": f"Bearer {sender_token}"}

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # 2. Trigger two concurrent requests
        tasks = [
            client.post("/banking/transfer", json=payload, headers=headers),
            client.post("/banking/transfer", json=payload, headers=headers),
        ]

        responses = await asyncio.gather(*tasks)

    # 3. Analyze results
    status_codes = [r.status_code for r in responses]

    # We expect exactly one 201 (Created) and one 402 (Payment Required)
    assert 201 in status_codes
    assert 402 in status_codes
    print("✅ Double-spend prevented successfully.")
