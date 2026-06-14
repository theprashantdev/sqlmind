import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "SQLMind"


@pytest.mark.asyncio
async def test_query_no_db_url(client):
    r = await client.post("/api/query", json={"question": "Show all users"})
    assert r.status_code == 400
    assert "No database URL" in r.json()["detail"]


@pytest.mark.asyncio
async def test_query_full_flow_mocked(client):
    mock_schema = {"users": {"columns": [{"name": "id", "type": "INTEGER"}], "foreign_keys": []}}
    mock_sql = "SELECT id FROM users LIMIT 1000"
    mock_result = {"columns": ["id"], "rows": [{"id": 1}], "row_count": 1, "execution_ms": 3}
    with patch("app.routes.query.introspect_schema", return_value=mock_schema), \
         patch("app.routes.query.generate_sql", new_callable=AsyncMock, return_value=mock_sql), \
         patch("app.routes.query.execute_query", return_value=mock_result):
        r = await client.post("/api/query", json={"question": "Show all users", "database_url": "sqlite:///test.db"})
    assert r.status_code == 200
    data = r.json()
    assert data["sql"] == mock_sql
    assert data["row_count"] == 1


@pytest.mark.asyncio
async def test_query_unsafe_sql_blocked(client):
    mock_schema = {"users": {"columns": [], "foreign_keys": []}}
    with patch("app.routes.query.introspect_schema", return_value=mock_schema), \
         patch("app.routes.query.generate_sql", new_callable=AsyncMock, return_value="DROP TABLE users"):
        r = await client.post("/api/query", json={"question": "delete everything", "database_url": "sqlite:///test.db"})
    assert r.status_code == 400
    assert "Unsafe SQL" in r.json()["detail"]


@pytest.mark.asyncio
async def test_schema_db_failure(client):
    with patch("app.routes.query.introspect_schema", side_effect=Exception("connection refused")):
        r = await client.post("/api/schema", json={"question": "x", "database_url": "postgresql://bad/none"})
    assert r.status_code == 400
    assert "connection refused" in r.json()["detail"]
