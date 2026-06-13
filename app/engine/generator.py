import httpx
import json
from app.core.config import settings

SQL_SYSTEM_PROMPT = """You are a SQL expert. Given a database schema and a natural language question, generate a single, correct, optimized SQL query.

Rules:
- Output ONLY valid SQL, nothing else
- Only use SELECT statements
- Use proper JOINs based on foreign key relationships
- Add LIMIT 1000 if the query could return many rows
- Use the exact table and column names from the schema provided"""

async def generate_sql(question: str, schema_text: str, dialect: str = "postgresql") -> str:
    user_prompt = f"Database dialect: {dialect}\n\nSchema:\n{schema_text}\n\nQuestion: {question}\n\nSQL query:"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json"},
            json={
                "model": settings.openrouter_model,
                "messages": [
                    {"role": "system", "content": SQL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.0,
            }
        )
        response.raise_for_status()
        sql = response.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown code blocks if present
        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        return sql.strip()
