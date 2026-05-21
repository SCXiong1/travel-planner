"""回收站路由"""

from fastapi import APIRouter, Request, HTTPException
from services import recycle_service

router = APIRouter(prefix="/api", tags=["recycle-bin"])


@router.get("/recycle-bin")
async def list_deleted_global(request: Request):
    return recycle_service.list_deleted(request.state.db)


@router.get("/trips/{trip_id}/recycle-bin")
async def list_deleted(request: Request, trip_id: int):
    return recycle_service.list_deleted(request.state.db, trip_id)


@router.post("/recycle-bin/{item_type}/{item_id}/restore")
async def restore(request: Request, item_type: str, item_id: int):
    if item_type not in ("trip", "day", "activity", "packing"):
        raise HTTPException(400, "无效的类型")
    ok = recycle_service.restore(request.state.db, item_type, item_id)
    if not ok:
        raise HTTPException(404, "未找到该已删除项")
    return {"ok": True}


@router.delete("/recycle-bin/{item_type}/{item_id}")
async def permanent_delete(request: Request, item_type: str, item_id: int):
    if item_type not in ("trip", "day", "activity", "packing"):
        raise HTTPException(400, "无效的类型")
    ok = recycle_service.permanent_delete(request.state.db, item_type, item_id)
    if not ok:
        raise HTTPException(404, "未找到该已删除项")
    return {"ok": True}
