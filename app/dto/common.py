from typing import Union, List
from pydantic import BaseModel


class BaseResponse(BaseModel):
    error_code: int = 0
    message: str = ''


class BaseResponseData(BaseResponse):
    data: Union[dict, str, int, List[dict], None] = None


class BasePaginationResponseData(BaseResponse):
    total: int = 0
    page: int = 0
    size: int = 0
    items: List = []