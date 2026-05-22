"""旅行计划路由"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services import trip_service


class CreateTripBody(BaseModel):
    title: str
    destination: str
    start_date: str
    end_date: str


class ReorderItem(BaseModel):
    id: int
    sort_order: int


router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("")
async def create(request: Request, body: CreateTripBody):
    return trip_service.create_trip(request.state.db, body.model_dump())


@router.get("")
async def list_all(request: Request):
    return trip_service.list_trips(request.state.db)


@router.get("/{trip_id}")
async def get_one(request: Request, trip_id: int):
    trip = trip_service.get_trip(request.state.db, trip_id)
    if not trip:
        raise HTTPException(404, "旅行计划不存在")
    return trip


@router.put("/reorder")
async def reorder(request: Request, body: list[ReorderItem]):
    trip_service.reorder_trips(request.state.db, [item.model_dump() for item in body])
    return {"ok": True}


@router.put("/{trip_id}")
async def update(request: Request, trip_id: int, body: CreateTripBody):
    trip = trip_service.update_trip(request.state.db, trip_id, body.model_dump())
    if not trip:
        raise HTTPException(404, "旅行计划不存在")
    return trip


@router.delete("/{trip_id}")
async def delete(request: Request, trip_id: int):
    ok = trip_service.delete_trip(request.state.db, trip_id)
    if not ok:
        raise HTTPException(404, "旅行计划不存在")
    return {"ok": True}
