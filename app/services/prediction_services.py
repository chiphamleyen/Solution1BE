import logging
from datetime import datetime
import io
from typing import List

import pandas as pd

from app.models.history import History, ClassifierEnum, ApprovalEnum
from app.models.user import UserRoleEnum
from app.helpers.prediction import get_prediction
from app.dto.report_dto import HistoryResponseDataWihtoutId
from app.helpers.exceptions import BadRequestException

_logger = logging.getLogger(__name__)

class PredictionService:
    @staticmethod
    async def save_prediction(
        list_of_prediction: List[History],
    ):
        await History.insert_many(list_of_prediction)
        prediction_data = []
        for prediction in list_of_prediction:
            prediction_data.append(HistoryResponseDataWihtoutId(**prediction.model_dump()))
        return prediction_data
    
    @staticmethod
    async def get_prediction(file: bytes, user_id: str, role: str):
        df = pd.read_csv(io.BytesIO(file), encoding='utf-8', sep=",")
        if 'url' not in df.columns:
            raise BadRequestException("File format is not correct")
        _logger.info(df.head())
        # try:
        prediction_df = get_prediction(df)
        # except Exception as e:
        #     _logger.error(f"Error in prediction: {e}")
        #     raise ValueError("File format is not correct")

        history_data = []
        approved_status = ApprovalEnum.Approved if role == UserRoleEnum.ADMIN.value else None
        for index, row in prediction_df.iterrows():
            history = History(
                submitter_id=user_id,
                submitter_role=role,
                original_url=row['url'],
                detection=bool(row['detection']),
                classifier=ClassifierEnum[row['classifier']],
                need_review=False,
                approved=approved_status,
                approved_at=None,
                approved_by=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            history_data.append(history)

        prediction_data = await PredictionService.save_prediction(history_data)
        return prediction_data
    
    