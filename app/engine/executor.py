import time
from sqlalchemy import create_engine, text
from app.core.config import settings

def execute_query(database_url: str, sql: str) -> dict:
    """Execute a validated SELECT query and return results."""
    engine = create_engine(database_url, connect_args={"connect_timeout": settings.query_timeout})
    start = time.monotonic()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchmany(settings.max_rows)]
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return {"columns": columns, "rows": rows, "row_count": len(rows), "execution_ms": elapsed_ms}
    finally:
        engine.dispose()
