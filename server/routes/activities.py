"""活动管理路由"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from services import activity_service


class ExpenseItem(BaseModel):
    amount: float
    payer: str
    split: str


class CreateActivityBody(BaseModel):
    type: str
    name: str
    location: str = ""
    start_time: str = ""
    end_time: str = ""
    need_reservation: bool = False
    reservation_detail: str = ""
    expense_items: list[ExpenseItem] = []
    sd_review: str = ""
    sg_review: str = ""


class UpdateActivityBody(BaseModel):
    type: str | None = None
    name: str | None = None
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    need_reservation: bool | None = None
    reservation_detail: str | None = None
    expense_items: list[ExpenseItem] | None = None
    sd_review: str | None = None
    sg_review: str | None = None


class ReorderItem(BaseModel):
    id: int
    sort_order: int


router = APIRouter(prefix="/api/trips/{trip_id}/days/{day_id}/activities", tags=["activities"])


@router.post("")
async def create(request: Request, trip_id: int, day_id: int, body: CreateActivityBody):
    act = activity_service.create_activity(request.state.db, day_id, body.model_dump(), request.state.user)
    await request.app.state.ws_manager.broadcast(trip_id, "activity_created", act)
    return act


@router.get("")
async def list_all(request: Request, trip_id: int, day_id: int):
    return activity_service.list_activities(request.state.db, day_id)


@router.put("/reorder")
async def reorder(request: Request, trip_id: int, day_id: int, body: list[ReorderItem]):
    activity_service.reorder_activities(request.state.db, day_id, [item.model_dump() for item in body])
    await request.app.state.ws_manager.broadcast(trip_id, "activities_reordered", {"day_id": day_id})
    return {"ok": True}


@router.put("/{act_id}")
async def update(request: Request, trip_id: int, day_id: int, act_id: int, body: UpdateActivityBody):
    act = activity_service.update_activity(
        request.state.db, act_id,
        {k: v for k, v in body.model_dump().items() if v is not None},
        request.state.user,
    )
    if not act:
        raise HTTPException(404, "活动不存在")
    await request.app.state.ws_manager.broadcast(trip_id, "activity_updated", act)
    return act


@router.delete("/{act_id}")
async def delete(request: Request, trip_id: int, day_id: int, act_id: int):
    ok = activity_service.delete_activity(request.state.db, act_id)
    if not ok:
        raise HTTPException(404, "活动不存在")
    await request.app.state.ws_manager.broadcast(trip_id, "activity_deleted", {"id": act_id})
    return {"ok": True}
