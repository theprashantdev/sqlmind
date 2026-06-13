from sqlalchemy import create_engine, inspect, text
from typing import Dict, List

def introspect_schema(database_url: str) -> Dict[str, List[dict]]:
    """Read all tables and columns from the target database."""
    engine = create_engine(database_url)
    inspector = inspect(engine)
    schema = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        schema[table_name] = {
            "columns": [{"name": c["name"], "type": str(c["type"])} for c in columns],
            "foreign_keys": [{"column": fk["constrained_columns"], "references": f"{fk['referred_table']}.{fk['referred_columns']}"} for fk in foreign_keys]
        }
    engine.dispose()
    return schema

def schema_to_prompt_text(schema: dict) -> str:
    """Format schema dict into a readable string for the LLM prompt."""
    lines = []
    for table, info in schema.items():
        cols = ", ".join(f"{c['name']} ({c['type']})" for c in info["columns"])
        lines.append(f"Table: {table}\n  Columns: {cols}")
        for fk in info.get("foreign_keys", []):
            lines.append(f"  FK: {fk['column']} -> {fk['references']}")
    return "\n".join(lines)
