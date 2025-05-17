from app.dto.common import BaseResponse
from fastapi import APIRouter


router = APIRouter(tags=['Ping'])


@router.get(
    '/ping',
    response_model=BaseResponse
)
async def check_health():
    return BaseResponse(
        message='Server is working'
    )