import logging
from datetime import datetime
from typing import List, Optional

from app.models.history import History, ClassifierEnum, ApprovalEnum
from app.dto.report_dto import ReportResponseData, ClassifierResponseData

_logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    async def get_report_data(min_date: datetime, max_date: datetime, user_id: Optional[str] = None):
        if user_id is not None:
            query = History.find(
                History.submitter_id == user_id,
                History.created_at >= min_date,
                History.created_at <= max_date
            )
        else:
            query = History.find(
                History.approved == ApprovalEnum.Approved,
                History.created_at >= min_date,
                History.created_at <= max_date
            )
        
        # Get aggregated data
        query_copy = query.clone()
        report_data = ReportResponseData()
        report_data.total = await query.count()

        # Get detection data
        report_data.detection_benign = await query_copy.find(History.detection == False).count()
        query_copy = query.clone()
        report_data.detection_malware = await query_copy.find(History.detection == True).count()
        query_copy = query.clone()

        # Get classifier data
        report_data.classifier = []
        for enum_value in ClassifierEnum:
            classifier_data = ClassifierResponseData(
                type=enum_value.value,
                total=await query_copy.find(History.classifier == enum_value.value).count()
            )
            query_copy = query.clone()
            report_data.classifier.append(classifier_data)
        return report_data