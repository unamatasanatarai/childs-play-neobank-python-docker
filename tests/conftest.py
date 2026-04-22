import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session.
    This prevents 'attached to a different loop' RuntimeErrors with asyncpg and SQLAlchemy.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
