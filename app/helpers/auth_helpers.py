import time
import jwt

from config.config import get_settings
from fastapi import Depends, Request, WebSocket
from fastapi.security import OAuth2AuthorizationCodeBearer

from app.helpers.exceptions import PermissionDeniedException

settings = get_settings()
default_secret_key = settings.secret_key
default_algorithm = settings.algorithms

def generate_token(
    payload=None, secret_key=default_secret_key,
    algorithm=default_algorithm,
):
    payload = payload or {}
    access_token = jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
    )
    if isinstance(access_token, str):
        return access_token
    else :
        return access_token.decode('utf-8')

def decode_token(
    encoded_token, secret_key=default_secret_key,
    algorithm=default_algorithm
):
    try:
        data = jwt.decode(
            encoded_token, secret_key,
            algorithms=[algorithm],
        )
        return data
    except jwt.ExpiredSignatureError:
        raise PermissionDeniedException(
            'Signature expired. Please log in again.'
        )
    except jwt.InvalidTokenError as e:
        print(repr(e))
        raise PermissionDeniedException('Invalid token. Please log in again.')
    
def login_token(user_id: str, role: str):
    payload = {
        "sub": role,
        "id": user_id,
        "exp": round(time.time()) + 86400, # 1 day expire
    }
    return generate_token(payload, default_secret_key)

class CustomOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        return await super().__call__(request or websocket)

oauth2_scheme = CustomOAuth2AuthorizationCodeBearer(authorizationUrl="token", tokenUrl="token", refreshUrl="token")
    
def get_current_user(token: str= Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise PermissionDeniedException(
            'Signature expired. Please log in again.'
        )
    return user.get("id"), user.get("sub")
