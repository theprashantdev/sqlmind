# 🧠 SQLMind

> Type what you want. Get SQL. See the data.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)]()
[![LangChain](https://img.shields.io/badge/LangChain-0.2-orange?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

## What It Does

SQLMind lets any user — technical or not — query any database by describing what they want in plain English.

**Input:** `"Show me the top 10 customers by total order value this year, with their email"`

**Output:**
```sql
SELECT c.name, c.email, SUM(o.total) AS total_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE EXTRACT(YEAR FROM o.created_at) = 2026
GROUP BY c.id, c.name, c.email
ORDER BY total_value DESC
LIMIT 10;
```

Plus: the actual query results, in table form.

## How It Works

1. **Schema Introspection** — SQLMind reads your database schema automatically (table names, columns, types, relationships)
2. **Prompt Engineering** — schema + user question are structured into a precise LLM prompt
3. **SQL Generation** — LLM generates syntactically correct, optimized SQL for your specific DB dialect
4. **Safety Check** — only SELECT statements are allowed; all writes blocked
5. **Execution** — query runs against your DB, results returned as JSON

## Quick Start

```bash
git clone https://github.com/theprashantdev/sqlmind
cd sqlmind
pip install -r requirements.txt
cp .env.example .env  # fill in DB URL + OpenRouter key
uvicorn app.main:app --reload
```

## API

### `POST /api/query`

```json
{
  "question": "Which products have not been ordered in the last 30 days?",
  "database_url": "postgresql://user:pass@host:5432/mydb"
}
```

**Response:**
```json
{
  "question": "Which products have not been ordered in the last 30 days?",
  "sql": "SELECT p.id, p.name FROM products p WHERE p.id NOT IN (SELECT DISTINCT product_id FROM orders WHERE created_at > NOW() - INTERVAL '30 days');",
  "results": [...],
  "row_count": 14,
  "execution_ms": 23
}
```

### `POST /api/schema`
Introspect any database and return its schema.

### `GET /api/history`
Full query history with SQL and results.

## Safety Model

- ✅ SELECT statements only
- ❌ INSERT / UPDATE / DELETE / DROP / TRUNCATE — all blocked at parse level
- ✅ Query timeout: 10 seconds max
- ✅ Result limit: 1000 rows max
- ✅ SQL injection prevention via parameterized execution

## Supported Databases

- PostgreSQL
- MySQL
- SQLite
- (Extensible — any SQLAlchemy-compatible DB)

## Project Structure

```
sqlmind/
├── app/
│   ├── main.py
│   ├── routes/
│   │   ├── query.py       # NL query endpoint
│   │   └── schema.py      # Schema introspection
│   ├── engine/
│   │   ├── introspector.py  # DB schema reader
│   │   ├── generator.py     # NL → SQL via LLM
│   │   ├── executor.py      # Safe query execution
│   │   └── safety.py        # SQL safety validator
│   └── core/config.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT © [Prashant Raj](https://github.com/theprashantdev)
