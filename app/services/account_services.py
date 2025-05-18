import logging
import hashlib
from datetime import datetime
from typing import List
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.models.user import User, UserRoleEnum
from app.dto.auth_dto import UserResponseData
from app.helpers.exceptions import NotFoundException, BadRequestException, PermissionDeniedException
from app.helpers.auth_helpers import login_token

_logger = logging.getLogger(__name__)


class AccountService:
    @staticmethod
    async def login(email: str, password: str, expected_role: str) -> User:
        user = await User.find_one({"email": email})
        if not user:
            raise PermissionDeniedException("Wrong email or password")
        if user.password != hashlib.sha256(password.encode()).hexdigest():
            raise PermissionDeniedException("Wrong email or password")
        if user.role.value != expected_role:
            raise PermissionDeniedException("Wrong role for this user")
        access_token = login_token(str(user.id), user.role.value)
        return access_token
    
    @staticmethod
    async def signup(user_name: str, email: str, password: str) -> User:
        new_user = User(
            user_name=user_name,
            email=email,
            role=UserRoleEnum.USER,
            password=hashlib.sha256(password.encode()).hexdigest(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        try:
            await new_user.save()
        except DuplicateKeyError:
            raise BadRequestException("Email already registered")
        _logger.info(f"New user created: {new_user.user_name}")
        return new_user
    
    @staticmethod
    async def create_new_admin(user_name: str, email: str, password: str) -> User:
        new_user = User(
            user_name=user_name,
            email=email,
            role=UserRoleEnum.ADMIN,
            password=hashlib.sha256(password.encode()).hexdigest(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        try:
            await new_user.save()
        except DuplicateKeyError:
            raise BadRequestException("Email already registered")
        _logger.info(f"New admin created: {new_user.user_name}")
        return new_user
    
    @staticmethod
    async def get_list_users(page: int, size: int) -> tuple[List[UserResponseData], int]:
        if page < 1 or size < 1:
            raise BadRequestException("Page and size must be greater than 0")
        skip = (page - 1) * size
        count = await User.count()
        users = await User.find_all(skip=skip, limit=size).project(UserResponseData).to_list()
        if not users:
            raise NotFoundException("No users found")
        return users, count
    
    @staticmethod
    async def update_user(user_id: str, user_name: str, email: str) -> UserResponseData:
        user = await User.find_one({"_id": PydanticObjectId(user_id)})
        if not user:
            raise NotFoundException(f"User not found")
        user.user_name = user_name
        user.email = email
        user.updated_at = datetime.now()
        try:
            await user.save()
        except DuplicateKeyError:
            raise BadRequestException("Email already registered")
        _logger.info(f"User updated: {user.user_name}")
        return UserResponseData(
            id=user.id,
            _id=user.id,
            user_name=user.user_name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> UserResponseData:
        user = await User.find_one({"_id": PydanticObjectId(user_id)}).project(UserResponseData)
        if not user:
            raise NotFoundException(f"User not found")
        return user
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        user = await User.find_one({"_id": PydanticObjectId(user_id)})
        if not user:
            raise NotFoundException(f"User not found")
        await user.delete()
        _logger.info(f"User deleted: {user.user_name}")
        return True