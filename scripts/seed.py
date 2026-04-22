import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.auth.models import User
from app.banking.models import Account
from app.auth.utils import hash_password


async def seed_data():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            print("🌱 Starting database seeding...")

            for i in range(1, 6):
                email = f"user{i}@example.com"

                # 1. Create User
                user = User(email=email, password_hash=hash_password("password123"))
                session.add(user)
                await session.flush()

                # 2. Create Account with 100.00 USD (10,000 cents)
                account = Account(
                    user_id=user.id, balance=10000, account_number=f"CHPAY-SEED-000{i}"
                )
                session.add(account)

            print("✅ Created 5 seeded users with 10,000 units each.")


if __name__ == "__main__":
    asyncio.run(seed_data())
