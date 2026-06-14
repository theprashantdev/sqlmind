from app.engine.safety import validate_sql

def test_select_allowed():
    is_safe, msg = validate_sql("SELECT * FROM users WHERE id = 1")
    assert is_safe
    assert msg == "ok"

def test_delete_blocked():
    is_safe, msg = validate_sql("DELETE FROM users WHERE id = 1")
    assert not is_safe
    assert "DELETE" in msg

def test_drop_blocked():
    is_safe, msg = validate_sql("DROP TABLE users")
    assert not is_safe

def test_insert_blocked():
    is_safe, msg = validate_sql("INSERT INTO users (name) VALUES ('hack')")
    assert not is_safe

def test_update_blocked():
    is_safe, msg = validate_sql("UPDATE users SET name='x' WHERE id=1")
    assert not is_safe

def test_truncate_blocked():
    is_safe, msg = validate_sql("TRUNCATE TABLE users")
    assert not is_safe

def test_complex_select_allowed():
    sql = "SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id ORDER BY 2 DESC LIMIT 10"
    is_safe, msg = validate_sql(sql)
    assert is_safe

def test_empty_sql_blocked():
    is_safe, msg = validate_sql("")
    assert not is_safe
