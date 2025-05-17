from datetime import datetime
from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from app.dto.common import BaseResponseData

class HistoryResponseDataWihtoutId(BaseModel):
    original_url: str
    detection: bool
    classifier: str
    need_review: bool
    approved: Optional[str]
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    created_at: datetime

class HistoryResponseWithoutId(BaseResponseData):
    data: HistoryResponseDataWihtoutId

class HistoryResponseData(HistoryResponseDataWihtoutId):
    id: PydanticObjectId = Field(alias='_id')
    original_url: str
    detection: bool
    classifier: str
    need_review: bool
    approved: Optional[str]
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    created_at: datetime

class HistoryResponse(BaseResponseData):
    data: HistoryResponseData

class ClassifierResponseData(BaseModel):
    type: str
    total: int

class ReportResponseData(BaseModel):
    total: int = 0
    detection_benign: int = 0
    detection_malware: int = 0
    classifier: List[ClassifierResponseData] = []

class ReportResponse(BaseResponseData):
    data: ReportResponseData