from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel, RootEnum

class UserRoleEnum(RootEnum):
    ADMIN = "admin"
    USER = "user"

class User(RootModel):
    class Settings:
        name = "user"
        indexes = [
            IndexModel(
                [
                    ("email", ASCENDING),
                ],
                unique=True,
            )
        ]
    email: str
    password: str
    user_name: str
    role: UserRoleEnum