"""活动业务逻辑"""

from fastapi import HTTPException
from services import expense_service


def _attach_expenses(db, act: dict) -> dict:
    act["expense_items"] = expense_service.get_by_activity(db, act["id"])
    act["expense_total"] = expense_service.sum_by_activity(db, act["id"])
    return act


def create_activity(db, day_id: int, data: dict, user: str = "") -> dict:
    st = data.get("start_time", "")
    et = data.get("end_time", "")
    if st and et and st > et:
        raise HTTPException(400, "开始时间不能晚于结束时间")

    max_order = db.execute(
        "SELECT COALESCE(MAX(sort_order), -1) FROM activities WHERE day_id = ? AND deleted_at IS NULL",
        (day_id,),
    ).fetchone()[0]

    need_res = 1 if data.get("need_reservation") else 0
    sd_review = data.get("sd_review", "") if user == "sd" else ""
    sg_review = data.get("sg_review", "") if user == "sg" else ""

    cursor = db.execute(
        """INSERT INTO activities (day_id, type, name, location, start_time, end_time, sort_order,
           need_reservation, reservation_detail, sd_review, sg_review)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (day_id, data["type"], data["name"],
         data.get("location", ""), data.get("start_time", ""), data.get("end_time", ""),
         max_order + 1,
         need_res, data.get("reservation_detail", ""),
         sd_review, sg_review),
    )
    db.commit()
    act = dict(db.execute("SELECT * FROM activities WHERE id = ?", (cursor.lastrowid,)).fetchone())

    items = data.get("expense_items")
    if items:
        act["expense_items"] = expense_service.create_items(db, act["id"], items)
        act["expense_total"] = sum(e["amount"] for e in act["expense_items"])
    else:
        act["expense_items"] = []
        act["expense_total"] = 0

    return act


def list_activities(db, day_id: int) -> list[dict]:
    acts = [dict(a) for a in db.execute(
        "SELECT * FROM activities WHERE day_id = ? AND deleted_at IS NULL ORDER BY sort_order",
        (day_id,),
    ).fetchall()]

    if not acts:
        return []

    ids = [a["id"] for a in acts]
    placeholders = ",".join("?" * len(ids))
    rows = db.execute(
        f"SELECT * FROM expense_items WHERE activity_id IN ({placeholders}) ORDER BY id",
        ids,
    ).fetchall()

    grouped: dict[int, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r["activity_id"], []).append(dict(r))

    for a in acts:
        a["expense_items"] = grouped.get(a["id"], [])
        a["expense_total"] = sum(e["amount"] for e in a["expense_items"])

    return acts


def get_activity(db, act_id: int) -> dict | None:
    act = db.execute(
        "SELECT * FROM activities WHERE id = ? AND deleted_at IS NULL", (act_id,)
    ).fetchone()
    if not act:
        return None
    return _attach_expenses(db, dict(act))


def _activity_exists(db, act_id: int) -> bool:
    row = db.execute(
        "SELECT 1 FROM activities WHERE id = ? AND deleted_at IS NULL", (act_id,)
    ).fetchone()
    return row is not None


def update_activity(db, act_id: int, data: dict, user: str = "") -> dict | None:
    if not _activity_exists(db, act_id):
        return None

    if user == "sd":
        data.pop("sg_review", None)
    elif user == "sg":
        data.pop("sd_review", None)

    # 校验时间：合并 data 和已有记录的值后比较
    existing = dict(db.execute("SELECT start_time, end_time FROM activities WHERE id = ?", (act_id,)).fetchone())
    st = data.get("start_time", existing["start_time"])
    et = data.get("end_time", existing["end_time"])
    if st and et and st > et:
        raise HTTPException(400, "开始时间不能晚于结束时间")

    fields = []
    values = []
    for key in ("type", "name", "location", "start_time", "end_time",
                 "need_reservation", "reservation_detail",
                 "sd_review", "sg_review"):
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
    if fields:
        values.append(act_id)
        db.execute(f"UPDATE activities SET {', '.join(fields)} WHERE id = ?", values)
        db.commit()

    if "expense_items" in data:
        expense_service.replace_items(db, act_id, data["expense_items"])

    return get_activity(db, act_id)


def delete_activity(db, act_id: int) -> bool:
    if not _activity_exists(db, act_id):
        return False
    db.execute(
        "UPDATE activities SET deleted_at = datetime('now', 'localtime') WHERE id = ?",
        (act_id,),
    )
    db.commit()
    return True


def reorder_activities(db, day_id: int, orders: list[dict]) -> bool:
    for item in orders:
        db.execute(
            "UPDATE activities SET sort_order = ? WHERE id = ? AND day_id = ? AND deleted_at IS NULL",
            (item["sort_order"], item["id"], day_id),
        )
    db.commit()
    return True
