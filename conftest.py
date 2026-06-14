import os
os.environ.setdefault("OPENROUTER_API_KEY", "dummy_key_for_ci")
os.environ.setdefault("DEFAULT_DATABASE_URL", "")
os.environ.setdefault("MAX_ROWS", "1000")
os.environ.setdefault("QUERY_TIMEOUT", "10")

import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
