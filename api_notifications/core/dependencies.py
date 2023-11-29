import json

import fastapi as fa
import httpx
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from core.enums import ServicesNamesEnum
from core.exceptions import UnauthorizedException
from core.logger_config import logger
from db import SessionLocalAsync, SessionLocal
from db.models.user import UserModel
from db.repository_async import SqlAlchemyRepositoryAsync
from db.repository_sync import SqlAlchemyRepositorySync
from services.notificator.notificator import Notificator


def session_sync_dependency():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def sqlalchemy_repo_sync_dependency():
    session = SessionLocal()
    repo = SqlAlchemyRepositorySync(session)
    try:
        yield repo
    finally:
        session.close()


async def sqlalchemy_repo_async_dependency() -> SqlAlchemyRepositoryAsync:
    try:
        async with SessionLocalAsync() as session:
            repo = SqlAlchemyRepositoryAsync(session)
            yield repo
    finally:
        await session.close()


async def notificator_dependency() -> Notificator:
    session = SessionLocal()
    try:
        repo = SqlAlchemyRepositorySync(session)
        notificator = Notificator(repo)
        yield notificator
    finally:
        session.close()


oauth2_scheme_local = OAuth2PasswordBearer(
    tokenUrl=f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/login")


async def verified_access_token_dependency(
        request: fa.Request,
        access_token: str = fa.Depends(oauth2_scheme_local),
) -> dict:
    url = f"http://{settings.API_AUTH_HOST}:{settings.API_AUTH_PORT}/api/v1/auth/verify-access-token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {
        'useragent': request.headers.get("user-agent"),
        'ip': request.headers.get('X-Forwarded-For'),
        'access_token': access_token,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=data)
    if resp.status_code != fa.status.HTTP_200_OK:
        raise UnauthorizedException
    return json.loads(resp.text)


async def verify_service_secret_dependency(
        request: fa.Request,
) -> None:
    auth_header = request.headers.get('Authorization')
    service_name = request.headers.get('Service-Name')
    if (not auth_header
            or service_name not in [s.value for s in ServicesNamesEnum]
            or auth_header != settings.SERVICE_TO_SERVICE_SECRET):
        detail = f"can't verify service request: {auth_header=:} {service_name=:}"
        logger.error(detail)
        raise UnauthorizedException(detail)


async def current_user_dependency(
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
        verified_token: dict = fa.Depends(verified_access_token_dependency)) -> UserModel:
    current_uuid = verified_token.get('sub')
    current_email = verified_token.get('email')
    return await repo.get_or_create_duplicated_user(current_uuid, current_email)
