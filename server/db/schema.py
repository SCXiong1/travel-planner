"""数据库建表"""


def init_db(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            destination TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            deleted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL REFERENCES trips(id),
            day_number INTEGER NOT NULL,
            date TEXT NOT NULL,
            title TEXT,
            deleted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_id INTEGER NOT NULL REFERENCES days(id),
            type TEXT NOT NULL CHECK(type IN ('eat', 'stay', 'transport', 'sight')),
            name TEXT NOT NULL,
            location TEXT,
            start_time TEXT,
            end_time TEXT,
            need_reservation INTEGER NOT NULL DEFAULT 0,
            reservation_detail TEXT,
            expense_amount REAL,
            expense_payer TEXT CHECK(expense_payer IN ('sd', 'sg')),
            expense_split TEXT CHECK(expense_split IN ('equal', 'assign')),
            sd_review TEXT DEFAULT '',
            sg_review TEXT DEFAULT '',
            sort_order INTEGER NOT NULL DEFAULT 0,
            deleted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS expense_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL REFERENCES activities(id),
            amount REAL NOT NULL,
            payer TEXT NOT NULL CHECK(payer IN ('sd', 'sg')),
            split TEXT NOT NULL CHECK(split IN ('equal', 'assign'))
        );

        CREATE TABLE IF NOT EXISTS packing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL REFERENCES trips(id),
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            assignee TEXT NOT NULL CHECK(assignee IN ('sd', 'sg')),
            checked INTEGER NOT NULL DEFAULT 0,
            sort_order INTEGER NOT NULL DEFAULT 0,
            deleted_at TEXT
        );
        """
    )
    conn.commit()


def migrate(conn):
    """增量迁移：sd_review/sg_review 列 + expense_items 表"""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(activities)").fetchall()]
    if "sd_review" not in cols:
        conn.execute("ALTER TABLE activities ADD COLUMN sd_review TEXT DEFAULT ''")
    if "sg_review" not in cols:
        conn.execute("ALTER TABLE activities ADD COLUMN sg_review TEXT DEFAULT ''")

    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='expense_items'"
    ).fetchall()]
    trip_cols = [r[1] for r in conn.execute("PRAGMA table_info(trips)").fetchall()]
    if "sort_order" not in trip_cols:
        conn.execute("ALTER TABLE trips ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")

    if not tables:
        conn.execute(
            """CREATE TABLE expense_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL REFERENCES activities(id),
                amount REAL NOT NULL,
                payer TEXT NOT NULL CHECK(payer IN ('sd', 'sg')),
                split TEXT NOT NULL CHECK(split IN ('equal', 'assign'))
            )"""
        )
    conn.commit()
