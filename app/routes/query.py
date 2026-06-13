import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engine.introspector import introspect_schema, schema_to_prompt_text
from app.engine.generator import generate_sql
from app.engine.executor import execute_query
from app.engine.safety import validate_sql
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["query"])

class QueryRequest(BaseModel):
    question: str
    database_url: str | None = None
    dialect: str = "postgresql"

@router.post("/query")
async def natural_language_query(req: QueryRequest):
    db_url = req.database_url or settings.default_database_url
    if not db_url:
        raise HTTPException(400, "No database URL provided")
    try:
        schema = introspect_schema(db_url)
    except Exception as e:
        raise HTTPException(400, f"Could not connect to database: {str(e)}")
    schema_text = schema_to_prompt_text(schema)
    sql = await generate_sql(req.question, schema_text, req.dialect)
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        raise HTTPException(400, f"Unsafe SQL generated: {reason}")
    try:
        result = execute_query(db_url, sql)
    except Exception as e:
        raise HTTPException(500, f"Query execution failed: {str(e)}")
    return {"question": req.question, "sql": sql, **result}

@router.post("/schema")
async def get_schema(req: QueryRequest):
    db_url = req.database_url or settings.default_database_url
    if not db_url:
        raise HTTPException(400, "No database URL provided")
    try:
        schema = introspect_schema(db_url)
    except Exception as e:
        raise HTTPException(400, f"Database connection failed: {str(e)}")
    return {"schema": schema, "table_count": len(schema)}
