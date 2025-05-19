import logging
from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId

from app.models.history import History, ApprovalEnum, ClassifierEnum
from app.dto.report_dto import HistoryResponseData
from app.helpers.exceptions import NotFoundException

_logger = logging.getLogger(__name__)

class HistoryService:
    @staticmethod
    async def get_by_id(history_id: str) -> HistoryResponseData:
        query = History.find_one(History.id == PydanticObjectId(history_id))
        return await query.project(HistoryResponseData)

    @staticmethod
    async def get_history_data(
        min_date: datetime, 
        max_date: datetime, 
        page: int, 
        size: int, 
        classifier: Optional[str] = None, 
        approved_status: Optional[str] = None, 
        need_review: Optional[bool] = None,
        user_id: Optional[str] = None
    ) -> tuple[List[HistoryResponseData], int]:
        if user_id is not None:
            query = History.find(
                History.submitter_id == user_id,
                History.created_at >= min_date,
                History.created_at <= max_date
            )
        else:
            query = History.find(
                History.created_at >= min_date,
                History.created_at <= max_date
            )
        if classifier is not None:
            query = query.find(History.classifier == ClassifierEnum[classifier])
        if approved_status is not None:
            query = query.find(History.approved == ApprovalEnum[approved_status])
        if need_review is not None:
            query = query.find(History.need_review == True)

        skip = (page - 1) * size
        count = await query.count()
        history_data = await query.skip(skip).limit(size).project(HistoryResponseData).to_list()
        return history_data, count
    
    @staticmethod
    async def get_recent_approval_history(page: int, size: int) -> tuple[List[HistoryResponseData], int]:
        query = History.find(
            History.need_review == True,
            History.approved == ApprovalEnum.Approved
        )
        skip = (page - 1) * size
        count = await query.count()
        history_data = await query.sort(-History.approved_at).skip(skip).limit(size).project(HistoryResponseData).to_list()
        return history_data, count
    
    @staticmethod
    async def user_submit_history(user_id: str, history_id: str) -> HistoryResponseData:
        history = await History.find_one(
            History.submitter_id == user_id, 
            History.id == PydanticObjectId(history_id)
        )
        if history is None:
            raise NotFoundException("History not found")
        history.need_review = True
        history.approved = ApprovalEnum.Pending
        history.updated_at = datetime.now()
        await history.save()
        return HistoryResponseData(**history.model_dump())
    
    @staticmethod
    async def update_history(history_id: str, approved: ApprovalEnum, admin_id: str) -> HistoryResponseData:
        history = await History.find_one(History.id == PydanticObjectId(history_id))
        if history is None:
            raise NotFoundException("History not found")
        history.approved = approved
        history.updated_at = datetime.now()
        history.approved_at = datetime.now()
        history.approved_by = admin_id
        await history.save()
        return HistoryResponseData(**history.model_dump())
    
    @staticmethod
    async def delete_history(history_id: str) -> bool:
        history = await History.find_one(History.id == PydanticObjectId(history_id))
        if history is None:
            raise NotFoundException("History not found")
        await history.delete()
        return True