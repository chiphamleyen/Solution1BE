from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.dto.common import BasePaginationResponseData, BaseResponse
from app.dto.report_dto import HistoryResponse
from app.models.user import UserRoleEnum
from app.models.history import ApprovalEnum
from app.services.history_services import HistoryService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['History'], prefix="/history")

@router.get(
    "/user_history",
    response_model=BasePaginationResponseData,
)
async def user_history(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    page: int = Query(1),
    size: int = Query(10),
    classifier: Optional[str] = Query(None),
    approved_status: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    history_data, total = await HistoryService.get_history_data(
        min_date=min_date, 
        max_date=max_date, 
        page=page, 
        size=size, 
        classifier=classifier,
        approved_status=approved_status,
        user_id=user_id
    )
    return BasePaginationResponseData(
        items=history_data,
        page=page,
        size=size,
        total=total
    )

@router.get(
    "/approved_global_history",
    response_model=BasePaginationResponseData,
)
async def approved_global_history(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    page: int = Query(1),
    size: int = Query(10),
    classifier: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
):
    history_data, total = await HistoryService.get_history_data(
        min_date=min_date, 
        max_date=max_date, 
        page=page, 
        size=size, 
        classifier=classifier,
        approved_status=ApprovalEnum.Approved.value,
        user_id=None
    )
    return BasePaginationResponseData(
        items=history_data,
        page=page,
        size=size,
        total=total
    )

@router.get(
    "/all_history",
    response_model=BasePaginationResponseData,
)
async def all_history(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    page: int = Query(1),
    size: int = Query(10),
    classifier: Optional[str] = Query(None),
    approved_status: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return BasePaginationResponseData(
            error_code=403,
            message="Permission denied"
        )
    history_data, total = await HistoryService.get_history_data(
        min_date=min_date,
        max_date=max_date,
        page=page,
        size=size,
        classifier=classifier,
        approved_status=approved_status,
        user_id=None
    )
    return BasePaginationResponseData(
        items=history_data,
        page=page,
        size=size,
        total=total
    )

@router.get(
    "/pending_approvals_history",
    response_model=BasePaginationResponseData,
)
async def pending_approvals_history(
    min_date: datetime = Query(...),
    max_date: datetime = Query(...),
    page: int = Query(1),
    size: int = Query(10),
    classifier: Optional[str] = Query(None),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return BasePaginationResponseData(
            error_code=403,
            message="Permission denied"
        )
    history_data, total = await HistoryService.get_history_data(
        min_date=min_date,
        max_date=max_date,
        page=page,
        size=size,
        classifier=classifier,
        approved_status=ApprovalEnum.Pending.value,
        need_review=True,
        user_id=None
    )
    return BasePaginationResponseData(
        items=history_data,
        page=page,
        size=size,
        total=total
    )

@router.get(
    "/recent_approvals_history",
    response_model=BasePaginationResponseData,
)
async def recent_approvals_history(
    page: int = Query(1),
    size: int = Query(10),
):
    history_data, total = await HistoryService.get_recent_approval_history(
        page=page,
        size=size
    )
    return BasePaginationResponseData(
        items=history_data,
        page=page,
        size=size,
        total=total
    )

@router.get(
    "/{history_id}",
    response_model=HistoryResponse,
)
async def get_by_id(
    history_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    history_data = await HistoryService.get_by_id(history_id)
    return HistoryResponse(
        message="Success",
        data=history_data
    )

@router.put(
    "/{history_id}/submit_for_approval",
    response_model=HistoryResponse,
)
async def submit_for_approval(
    history_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    history_data = await HistoryService.user_submit_history(
        history_id=history_id, 
        user_id=user_id)
    return HistoryResponse(
        message="Success",
        data=history_data
    )

@router.put(
    "/{history_id}/approve",
    response_model=HistoryResponse,
)
async def approve(
    history_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return HistoryResponse(
            error_code=403,
            message="Permission denied"
        )
    history_data = await HistoryService.update_history(history_id, ApprovalEnum.Approved, user_id)
    return HistoryResponse(
        message="Success",
        data=history_data
    )

@router.put(
    "/{history_id}/reject",
    response_model=HistoryResponse,
)
async def reject(
    history_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return HistoryResponse(
            error_code=403,
            message="Permission denied"
        )
    history_data = await HistoryService.update_history(history_id, ApprovalEnum.Rejected, user_id)
    return HistoryResponse(
        message="Success",
        data=history_data
    )

@router.delete(
    "/{history_id}",
    response_model=BaseResponse,
)
async def delete(
    history_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN.value:
        return BaseResponse(
            error_code=403,
            message="Permission denied"
        )
    history_data = await HistoryService.delete_history(history_id)
    return BaseResponse(
        message="Success"
    )