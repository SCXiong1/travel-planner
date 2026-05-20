"""结算路由"""

from fastapi import APIRouter, Request
from services import settlement_service

router = APIRouter(prefix="/api/trips/{trip_id}/settlement", tags=["settlement"])


@router.get("")
async def get_settlement(request: Request, trip_id: int):
    return settlement_service.get_settlement(request.state.db, trip_id)
