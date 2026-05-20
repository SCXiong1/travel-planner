"""天管理路由"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services import day_service


class CreateDayBody(BaseModel):
    date: str
    title: str = ""


class UpdateDayBody(BaseModel):
    date: str | None = None
    title: str | None = None


class ReorderItem(BaseModel):
    id: int
    day_number: int


router = APIRouter(prefix="/api/trips/{trip_id}/days", tags=["days"])


@router.post("")
async def create(request: Request, trip_id: int, body: CreateDayBody):
    return day_service.create_day(request.state.db, trip_id, body.model_dump())


@router.get("")
async def list_all(request: Request, trip_id: int):
    return day_service.list_days(request.state.db, trip_id)


@router.get("/{day_id}")
async def get_one(request: Request, trip_id: int, day_id: int):
    day = day_service.get_day(request.state.db, day_id)
    if not day:
        raise HTTPException(404, "天不存在")
    return day


@router.put("/reorder")
async def reorder(request: Request, trip_id: int, body: list[ReorderItem]):
    day_service.reorder_days(request.state.db, trip_id, [item.model_dump() for item in body])
    return {"ok": True}


@router.put("/{day_id}")
async def update(request: Request, trip_id: int, day_id: int, body: UpdateDayBody):
    day = day_service.update_day(request.state.db, day_id, {k: v for k, v in body.model_dump().items() if v is not None})
    if not day:
        raise HTTPException(404, "天不存在")
    return day


@router.delete("/{day_id}")
async def delete(request: Request, trip_id: int, day_id: int):
    ok = day_service.delete_day(request.state.db, day_id)
    if not ok:
        raise HTTPException(404, "天不存在")
    return {"ok": True}
