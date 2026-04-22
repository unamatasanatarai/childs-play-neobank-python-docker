from sqlalchemy import select, func
from app.banking.models import Account
from app.database import AsyncSessionLocal


async def test_ledger_sum_integrity():
    """
    Verifies that the total amount of money in the system is 50,000
    (assuming 5 users with 10,000 each).
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.sum(Account.balance)))
        total_balance = result.scalar()

        # Based on our seed data (5 users * 10,000)
        assert total_balance == 50000
        print(f"✅ System Integrity Confirmed: Total balance is {total_balance}")
