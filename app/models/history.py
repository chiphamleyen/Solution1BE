from pymongo import ASCENDING, IndexModel
from datetime import datetime
from typing import Optional

from app.models.base import RootModel, RootEnum
from app.models.user import UserRoleEnum

class ClassifierEnum(RootEnum):
    Phishing = "Phishing"
    Defacement = "Defacement"
    Malware = "Malware"
    Benign = "Benign"

class ApprovalEnum(RootEnum):
    Approved = "Approved"
    Rejected = "Rejected"
    Pending = "Pending"

class History(RootModel):
    class Settings:
        name = "history"
        indexes = [
            IndexModel(
                [
                    ("submitter_id", ASCENDING),
                ]
            )
        ]
    submitter_id: str #ID of the submitter
    submitter_role: UserRoleEnum
    original_url: str
    detection: bool
    classifier: ClassifierEnum
    # Attribute for submission and review below
    need_review: bool
    approved: Optional[ApprovalEnum]
    approved_at: Optional[datetime]
    approved_by: Optional[str] #ID of the approver