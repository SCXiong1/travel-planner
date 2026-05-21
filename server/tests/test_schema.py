"""测试数据库建表 —— 验证所有表和 deleted_at 字段"""

import sqlite3
import pytest
from db.schema import init_db


@pytest.fixture
def conn():
    """每次测试使用内存数据库"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_init_db_creates_all_tables(conn):
    """初始化后应创建 trips, days, activities, packing_items 四张表"""
    init_db(conn)

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [t["name"] for t in tables]

    assert "trips" in table_names
    assert "days" in table_names
    assert "activities" in table_names
    assert "packing_items" in table_names


def test_trips_table_has_required_columns(conn):
    """trips 表应包含基本字段"""
    init_db(conn)

    cols = conn.execute("PRAGMA table_info(trips)").fetchall()
    col_names = [c["name"] for c in cols]

    assert "id" in col_names
    assert "title" in col_names
    assert "destination" in col_names
    assert "start_date" in col_names
    assert "end_date" in col_names
    assert "created_at" in col_names
    assert "deleted_at" in col_names


def test_activities_table_has_required_columns(conn):
    """activities 表应包含类型、时间、开销、预约、评价等字段"""
    init_db(conn)

    cols = conn.execute("PRAGMA table_info(activities)").fetchall()
    col_names = [c["name"] for c in cols]

    assert "id" in col_names
    assert "day_id" in col_names
    assert "type" in col_names
    assert "name" in col_names
    assert "start_time" in col_names
    assert "end_time" in col_names
    assert "need_reservation" in col_names
    assert "reservation_detail" in col_names
    assert "expense_amount" in col_names
    assert "expense_payer" in col_names
    assert "expense_split" in col_names
    assert "sd_review" in col_names
    assert "sg_review" in col_names
    assert "sort_order" in col_names
    assert "deleted_at" in col_names


def test_packing_items_table_has_required_columns(conn):
    """packing_items 表应包含分类、负责人、勾选等字段"""
    init_db(conn)

    cols = conn.execute("PRAGMA table_info(packing_items)").fetchall()
    col_names = [c["name"] for c in cols]

    assert "id" in col_names
    assert "trip_id" in col_names
    assert "name" in col_names
    assert "category" in col_names
    assert "assignee" in col_names
    assert "checked" in col_names
    assert "sort_order" in col_names
    assert "deleted_at" in col_names


def test_can_insert_and_query_trip(conn):
    """建表后可正常插入和查询数据"""
    init_db(conn)

    conn.execute(
        "INSERT INTO trips (title, destination, start_date, end_date, created_at) "
        "VALUES (?, ?, ?, ?, datetime('now'))",
        ("日本行", "东京", "2026-06-01", "2026-06-07"),
    )
    conn.commit()

    trip = conn.execute("SELECT * FROM trips WHERE id = 1").fetchone()
    assert trip["title"] == "日本行"
    assert trip["destination"] == "东京"
    assert trip["created_at"] is not None
    assert trip["deleted_at"] is None
