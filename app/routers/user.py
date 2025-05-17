from fastapi import APIRouter, Depends, Query

from app.dto.common import BaseResponse, BasePaginationResponseData
from app.dto.auth_dto import SignUpRequest, UserResponse, UserProfileRequest
from app.models.user import UserRoleEnum
from app.services.account_services import AccountService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['User'], prefix="/user_management")

@router.get(
    '/list_users',
    response_model=BasePaginationResponseData
)
async def get_list_users(
    user: str = Depends(get_current_user),
    page: int = Query(1),
    size: int = Query(10),
):
    user_id, role = user
    if role != UserRoleEnum.ADMIN.value:
        return BasePaginationResponseData(
            message='Permission Denied',
            error_code=403
        )
    users, total = await AccountService.get_list_users(page, size)
    return BasePaginationResponseData(
        message='Succeed',
        items=users,
        total=total,
        page=page,
        size=size
    )

@router.get(
    '/{user_id}',
    response_model=UserResponse
)
async def get_user(
    user_id: str,
    user: str = Depends(get_current_user),
):
    user_id, role = user
    if role != UserRoleEnum.ADMIN.value:
        return UserResponse(
            message='Permission Denied',
            error_code=403
        )
    resp = await AccountService.get_user_by_id(user_id)
    return UserResponse(
        message='Succeed',
        data=resp
    )

@router.post(
    '/create_new_admin',
    response_model=BaseResponse
)
async def create_new_admin(
    data: SignUpRequest,
    user: str = Depends(get_current_user),
):
    user_id, role = user
    if role != UserRoleEnum.ADMIN.value:
        return UserResponse(
            message='Permission Denied',
            error_code=403
        )
    await AccountService.create_new_admin(
        user_name=data.user_name,
        email=data.email,
        password=data.password
    )
    return BaseResponse(
        message='Succeed',
        error_code=0
    )

@router.put(
    '/{user_id}'
)
async def update_user(
    user_id: str,
    data: UserProfileRequest,
    user: str = Depends(get_current_user),
):
    user_id, role = user
    if role != UserRoleEnum.ADMIN.value:
        return UserResponse(
            message='Permission Denied',
            error_code=403
        )
    resp = await AccountService.update_user(
        user_id=user_id,
        user_name=data.user_name,
        email=data.email,
    )
    return UserResponse(
        message='Succeed',
        error_code=0,
        data = resp
    )

@router.delete(
    '/{user_id}'
)
async def delete_user(
    user_id: str,
    user: str = Depends(get_current_user),
):
    user_id, role = user
    if role != UserRoleEnum.ADMIN.value:
        return BaseResponse(
            message='Permission Denied',
            error_code=403
        )
    await AccountService.delete_user(user_id)
    return BaseResponse(
        message='Succeed',
        error_code=0
    )
