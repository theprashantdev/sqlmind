import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "SQLMind"


@pytest.mark.asyncio
async def test_query_no_db_url_no_default():
    """Without a database URL and no default set, should return 400."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/api/query", json={"question": "Show all users"})
    assert r.status_code == 400
    assert "No database URL" in r.json()["detail"]


@pytest.mark.asyncio
async def test_query_full_flow_mocked():
    mock_schema = {"users": {"columns": [{"name": "id", "type": "INTEGER"}, {"name": "name", "type": "VARCHAR"}], "foreign_keys": []}}
    mock_sql = "SELECT id, name FROM users LIMIT 1000"
    mock_result = {"columns": ["id", "name"], "rows": [{"id": 1, "name": "Alice"}], "row_count": 1, "execution_ms": 4}

    with patch("app.routes.query.introspect_schema", return_value=mock_schema), \
         patch("app.routes.query.generate_sql", new_callable=AsyncMock, return_value=mock_sql), \
         patch("app.routes.query.execute_query", return_value=mock_result):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/query", json={
                "question": "Show all users",
                "database_url": "sqlite:///test.db"
            })
    assert r.status_code == 200
    data = r.json()
    assert data["sql"] == mock_sql
    assert data["row_count"] == 1
    assert data["rows"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_query_unsafe_sql_blocked():
    mock_schema = {"users": {"columns": [], "foreign_keys": []}}
    dangerous_sql = "DROP TABLE users"

    with patch("app.routes.query.introspect_schema", return_value=mock_schema), \
         patch("app.routes.query.generate_sql", new_callable=AsyncMock, return_value=dangerous_sql):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/query", json={
                "question": "Delete everything",
                "database_url": "sqlite:///test.db"
            })
    assert r.status_code == 400
    assert "Unsafe SQL" in r.json()["detail"]


@pytest.mark.asyncio
async def test_schema_db_connection_failure():
    with patch("app.routes.query.introspect_schema", side_effect=Exception("connection refused")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/schema", json={
                "question": "irrelevant",
                "database_url": "postgresql://bad:bad@localhost/none"
            })
    assert r.status_code == 400
    assert "connection refused" in r.json()["detail"]
