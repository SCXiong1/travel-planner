"""回收站业务逻辑"""

from fastapi import HTTPException

ENTITY_REGISTRY = [
    {
        "type": "trip",
        "table": "trips",
        "id_col": "id",
        "parents": [],
        "list_select": "id, title as name, deleted_at, 'trip' as type",
        "list_from": "trips",
        "list_where": "deleted_at IS NOT NULL",
        "trip_filter_col": "id",
    },
    {
        "type": "day",
        "table": "days",
        "id_col": "id",
        "parents": [
            {"fk": "trip_id", "parent_table": "trips", "parent_id_col": "id", "error": "请先恢复所属旅行"},
        ],
        "list_select": "d.id, (d.date || ' Day' || d.day_number) as name, d.deleted_at, 'day' as type, t.title as trip_title, d.trip_id",
        "list_from": "days d JOIN trips t ON d.trip_id = t.id",
        "list_where": "d.deleted_at IS NOT NULL",
        "list_order": "d.deleted_at DESC",
        "trip_filter_col": "d.trip_id",
    },
    {
        "type": "activity",
        "table": "activities",
        "id_col": "id",
        "parents": [
            {"fk": "day_id", "parent_table": "days", "parent_id_col": "id", "error": "请先恢复所属天"},
            {"fk_path_sql": "SELECT trip_id FROM days WHERE id = ?", "fk_path_args": ["day_id"], "parent_table": "trips", "parent_id_col": "id", "error": "请先恢复所属旅行"},
        ],
        "list_select": "a.id, a.name, a.deleted_at, 'activity' as type, d.date as day_date, d.day_number, d.trip_id, t.title as trip_title",
        "list_from": "activities a JOIN days d ON a.day_id = d.id JOIN trips t ON d.trip_id = t.id",
        "list_where": "a.deleted_at IS NOT NULL",
        "list_order": "a.deleted_at DESC",
        "trip_filter_col": "d.trip_id",
    },
    {
        "type": "packing",
        "table": "packing_items",
        "id_col": "id",
        "parents": [
            {"fk": "trip_id", "parent_table": "trips", "parent_id_col": "id", "error": "请先恢复所属旅行"},
        ],
        "list_select": "p.id, p.name, p.deleted_at, 'packing' as type, t.title as trip_title, p.trip_id",
        "list_from": "packing_items p JOIN trips t ON p.trip_id = t.id",
        "list_where": "p.deleted_at IS NOT NULL",
        "list_order": "p.deleted_at DESC",
        "trip_filter_col": "p.trip_id",
    },
]

_TYPE_TO_ENTRY = {e["type"]: e for e in ENTITY_REGISTRY}


def list_deleted(db, trip_id: int | None = None) -> list[dict]:
    items = []

    for entry in ENTITY_REGISTRY:
        where = entry["list_where"]
        params: tuple = ()
        if trip_id is not None:
            where += f" AND {entry['trip_filter_col']} = ?"
            params = (trip_id,)
        rows = db.execute(
            f"""SELECT {entry['list_select']}
                FROM {entry['list_from']}
                WHERE {where}
                ORDER BY {entry.get('list_order', 'deleted_at DESC')}""",
            params,
        ).fetchall()
        items.extend(dict(r) for r in rows)

    items.sort(key=lambda x: x["deleted_at"] or "", reverse=True)
    return items


def restore(db, item_type: str, item_id: int) -> bool:
    entry = _TYPE_TO_ENTRY.get(item_type)
    if not entry:
        return False

    item = db.execute(
        f"SELECT * FROM {entry['table']} WHERE {entry['id_col']} = ? AND deleted_at IS NOT NULL",
        (item_id,),
    ).fetchone()
    if not item:
        return False

    for parent in entry["parents"]:
        if "fk" in parent:
            parent_id = item[parent["fk"]]
        else:
            row = db.execute(parent["fk_path_sql"], [item[a] for a in parent["fk_path_args"]]).fetchone()
            if not row:
                continue
            parent_id = row[0]

        deleted_parent = db.execute(
            f"SELECT {parent['parent_id_col']} FROM {parent['parent_table']} WHERE {parent['parent_id_col']} = ? AND deleted_at IS NOT NULL",
            (parent_id,),
        ).fetchone()
        if deleted_parent:
            raise HTTPException(400, parent["error"])

    db.execute(f"UPDATE {entry['table']} SET deleted_at = NULL WHERE {entry['id_col']} = ?", (item_id,))
    db.commit()
    return True


def permanent_delete(db, item_type: str, item_id: int) -> bool:
    entry = _TYPE_TO_ENTRY.get(item_type)
    if not entry:
        return False

    item = db.execute(
        f"SELECT {entry['id_col']} FROM {entry['table']} WHERE {entry['id_col']} = ? AND deleted_at IS NOT NULL",
        (item_id,),
    ).fetchone()
    if not item:
        return False

    db.execute(f"DELETE FROM {entry['table']} WHERE {entry['id_col']} = ?", (item_id,))
    db.commit()
    return True
