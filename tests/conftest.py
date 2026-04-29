"""
Pytest fixtures for FastAPI backend tests.
"""
import pytest
import httpx
from src.app import app


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def client():
    """
    Create an async test client for the FastAPI application.
    Uses function scope to ensure clean state for each test.
    """
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
