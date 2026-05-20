"""打包清单路由"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services import packing_service


class CreateItemBody(BaseModel):
    name: str
    category: str
    assignee: str


class UpdateItemBody(BaseModel):
    name: str | None = None
    category: str | None = None
    assignee: str | None = None


router = APIRouter(prefix="/api/trips/{trip_id}/packing", tags=["packing"])


@router.post("")
async def create(request: Request, trip_id: int, body: CreateItemBody):
    item = packing_service.create_item(request.state.db, trip_id, body.model_dump())
    await request.app.state.ws_manager.broadcast(trip_id, "packing_created", item)
    return item


@router.get("")
async def list_all(request: Request, trip_id: int):
    return packing_service.list_items(request.state.db, trip_id)


@router.put("/{item_id}")
async def update(request: Request, trip_id: int, item_id: int, body: UpdateItemBody):
    item = packing_service.update_item(request.state.db, item_id,
                                       {k: v for k, v in body.model_dump().items() if v is not None})
    if not item:
        raise HTTPException(404, "物品不存在")
    await request.app.state.ws_manager.broadcast(trip_id, "packing_updated", item)
    return item


@router.put("/{item_id}/check")
async def toggle_check(request: Request, trip_id: int, item_id: int):
    item = packing_service.toggle_check(request.state.db, item_id)
    if not item:
        raise HTTPException(404, "物品不存在")
    await request.app.state.ws_manager.broadcast(trip_id, "packing_checked", item)
    return item


@router.delete("/{item_id}")
async def delete(request: Request, trip_id: int, item_id: int):
    ok = packing_service.delete_item(request.state.db, item_id)
    if not ok:
        raise HTTPException(404, "物品不存在")
    await request.app.state.ws_manager.broadcast(trip_id, "packing_deleted", {"id": item_id})
    return {"ok": True}
