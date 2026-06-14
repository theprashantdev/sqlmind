## Live Demo

https://sqlmind-lupf.onrender.com

API Docs:
https://sqlmind-lupf.onrender.com/docs

# SQLMind

> Describe the data you need in plain English. Get back an optimized SQL query, execute it, and see the results.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![CI](https://github.com/theprashantdev/sqlmind/actions/workflows/ci.yml/badge.svg)](https://github.com/theprashantdev/sqlmind/actions/workflows/ci.yml)

## What It Does

1. Connect SQLMind to any PostgreSQL, MySQL, or SQLite database
2. Ask a question in plain English: `"Show me the top 10 customers by total order value"`
3. SQLMind reads your schema, generates a correct SQL query, validates it is read-only, executes it, and returns the results
4. Every generated query is validated before execution — write operations (`DELETE`, `DROP`, `INSERT`, `UPDATE`, etc.) are blocked at the safety layer

## Quick Start

```bash
git clone https://github.com/theprashantdev/sqlmind
cd sqlmind
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** for interactive API docs.

## Environment Variables

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
DEFAULT_DATABASE_URL=postgresql://user:password@localhost:5432/mydb
MAX_ROWS=1000
QUERY_TIMEOUT=10
```

`DEFAULT_DATABASE_URL` is optional. If not set, callers must provide `database_url` in each request.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/query` | Ask a question, get SQL + results |
| `POST` | `/api/schema` | Inspect the schema of a connected database |
| `GET` | `/health` | Health check |

## Example Request

```bash
curl -X POST http://localhost:8000/api/query \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Top 5 customers by total order value",
    "database_url": "postgresql://user:pass@localhost/mydb"
  }'
```

```json
{
  "question": "Top 5 customers by total order value",
  "sql": "SELECT c.name, SUM(o.total) AS total_value FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id ORDER BY total_value DESC LIMIT 5",
  "columns": ["name", "total_value"],
  "rows": [{"name": "Acme Corp", "total_value": 142000}],
  "row_count": 5,
  "execution_ms": 12
}
```

## Safety

Every generated query is validated before execution. Only `SELECT` is permitted. Any query containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, or `EXEC` is rejected with a `400` error before it reaches the database.

## Running Tests

Tests use mocked LLM and database calls — no API key or live database needed.

```bash
pytest --tb=short -v
```

## Docker

```bash
docker build -t sqlmind .
docker run -p 8000:8000 --env-file .env sqlmind
```

## Architecture

```
POST /api/query
       │
       ▼
  Schema Introspection
  (read table/column structure from DB)
       │
       ▼
  SQL Generation
  (OpenRouter LLM — SELECT only)
       │
       ▼
  Safety Validation
  (block any non-SELECT keywords)
       │
       ▼
  Query Execution
  (return columns + rows + timing)
```

## Project Structure

```
sqlmind/
├── app/
│   ├── core/config.py        # Pydantic settings
│   ├── engine/
│   │   ├── generator.py      # OpenRouter SQL generation
│   │   ├── executor.py       # Query execution
│   │   ├── introspector.py   # Schema reading
│   │   └── safety.py         # SQL validation
│   ├── routes/query.py       # API routes
│   └── main.py
├── tests/
│   ├── test_safety.py
│   └── test_api.py
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```

## License

MIT © [Prashant Raj](https://github.com/theprashantdev)
