from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.dto.report_dto import ReportResponse
from app.models.user import UserRoleEnum
from app.services.report_services import ReportService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['Report'], prefix="/report")

@router.get(
    "/user_report",
    response_model=ReportResponse,
)
async def user_report(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    report = await ReportService.get_report_data(min_date, max_date, user_id)
    return ReportResponse(
        data=report
    )

@router.get(
    "/admin_report",
    response_model=ReportResponse,
)
async def admin_report(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return ReportResponse(
            error_code=403,
            message="Permission denied",
            data=None
        )
    
    report = await ReportService.get_report_data(min_date, max_date, None)
    return ReportResponse(
        data=report
    )