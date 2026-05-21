"""开销子表业务逻辑"""


def _build_items(activity_id: int, items: list[dict], cursors: list) -> list[dict]:
    results = []
    for item, c in zip(items, cursors):
        results.append({
            "id": c.lastrowid,
            "activity_id": activity_id,
            "amount": item["amount"],
            "payer": item["payer"],
            "split": item["split"],
        })
    return results


def create_items(db, activity_id: int, items: list[dict]) -> list[dict]:
    cursors = []
    for item in items:
        c = db.execute(
            "INSERT INTO expense_items (activity_id, amount, payer, split) VALUES (?, ?, ?, ?)",
            (activity_id, item["amount"], item["payer"], item["split"]),
        )
        cursors.append(c)
    db.commit()
    return _build_items(activity_id, items, cursors)


def get_by_activity(db, activity_id: int) -> list[dict]:
    rows = db.execute(
        "SELECT * FROM expense_items WHERE activity_id = ? ORDER BY id", (activity_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def sum_by_activity(db, activity_id: int) -> float:
    row = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expense_items WHERE activity_id = ?",
        (activity_id,),
    ).fetchone()
    return row[0]


def delete_by_activity(db, activity_id: int):
    db.execute("DELETE FROM expense_items WHERE activity_id = ?", (activity_id,))
    db.commit()


def replace_items(db, activity_id: int, items: list[dict]) -> list[dict]:
    db.execute("DELETE FROM expense_items WHERE activity_id = ?", (activity_id,))
    cursors = []
    for item in items:
        c = db.execute(
            "INSERT INTO expense_items (activity_id, amount, payer, split) VALUES (?, ?, ?, ?)",
            (activity_id, item["amount"], item["payer"], item["split"]),
        )
        cursors.append(c)
    db.commit()
    return _build_items(activity_id, items, cursors)
