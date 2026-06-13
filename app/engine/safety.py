import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DDL, DML

BLOCKED_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE", "REPLACE", "EXEC", "EXECUTE"}

def validate_sql(sql: str) -> tuple[bool, str]:
    """Returns (is_safe, reason). Only SELECT is allowed."""
    parsed = sqlparse.parse(sql)
    if not parsed:
        return False, "Empty or unparseable SQL"
    for statement in parsed:
        for token in statement.flatten():
            if token.ttype in (DDL, DML) or (token.ttype is Keyword and token.normalized.upper() in BLOCKED_KEYWORDS):
                if token.normalized.upper() != "SELECT":
                    return False, f"Blocked keyword detected: {token.normalized.upper()}"
    return True, "ok"
