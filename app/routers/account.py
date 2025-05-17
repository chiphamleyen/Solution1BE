from fastapi import APIRouter, Depends

from app.dto.common import BaseResponse
from app.dto.auth_dto import LoginRequest, LoginResponseData, LoginResponse, SignUpRequest, UserResponse, UserProfileRequest
from app.models.user import UserRoleEnum
from app.services.account_services import AccountService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['Account'], prefix="/account")

@router.post(
    '/user_login',
    response_model=LoginResponse
)
async def user_login(
    data: LoginRequest
):
    access_token = await AccountService.login(
        email=data.email, 
        password=data.password,
        expected_role=UserRoleEnum.USER.value
    )
    return LoginResponse(
        message='User Logged in',
        data=LoginResponseData(access_token=access_token)
    )

@router.post(
    '/admin_login',
    response_model=LoginResponse
)
async def admin_login(
    data: LoginRequest
):
    access_token = await AccountService.login(
        email=data.email, 
        password=data.password,
        expected_role=UserRoleEnum.ADMIN.value
    )
    return LoginResponse(
        message='Admin Logged in',
        data=LoginResponseData(access_token=access_token)
    )

@router.post(
    '/signup',
    response_model=BaseResponse
)
async def user_signup(
    data: SignUpRequest
):
    await AccountService.signup(
        user_name=data.user_name,
        email=data.email,
        password=data.password
    )
    return BaseResponse(
        message='Succeed',
        error_code=0
    )

@router.get(
    '/profile',
    response_model=UserResponse
)
async def get_current_user(
    user: str = Depends(get_current_user),
):
    user_id, role = user
    resp = await AccountService.get_user_by_id(user_id)
    return UserResponse(
        message='Succeed',
        data=resp
    )

@router.put(
    '/update_profile',
    response_model=UserResponse
)
async def update_profile(
    data: UserProfileRequest,
    user: str = Depends(get_current_user),
):
    user_id, role = user
    resp = await AccountService.update_user(
        user_id=user_id,
        user_name=data.user_name,
        email=data.email,
    )
    return UserResponse(
        message='Succeed',
        error_code=0,
        data=resp
    )
