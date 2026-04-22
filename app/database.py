import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

# Load connection string from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://admin:development_password@db:5432/childspay_ledger",
)

# 1. Create the Async Engine
# We use NullPool in some serverless/demo environments, but for a
# persistent container, the default QueuePool is fine.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging in development
    future=True,
)

# 2. Configure the Session Factory
# expire_on_commit=False prevents objects from being detached after commit
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 3. Base Class for Models
class Base(DeclarativeBase):
    pass


# 4. Dependency for FastAPI Routes
async def get_db():
    """
    Dependency that provides a database session to a request.
    Ensures the session is closed after the request is finished.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
