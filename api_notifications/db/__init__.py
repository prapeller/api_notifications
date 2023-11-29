from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings


def init_models():
    from db.models import celery_tasks  # noqa
    from db.models import user  # noqa
    from db.models import message  # noqa


DATABASE_NOTIFICATIONS_URL_ASYNC = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@' \
                                   f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'
engine_async = create_async_engine(DATABASE_NOTIFICATIONS_URL_ASYNC, future=True)
SessionLocalAsync = sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)

DATABASE_AUTH_URL_SYNC = f'postgresql+psycopg2://{settings.AUTH_POSTGRES_USER}:{settings.AUTH_POSTGRES_PASSWORD}@' \
                         f'{settings.AUTH_POSTGRES_HOST}:{settings.AUTH_POSTGRES_PORT}/{settings.AUTH_POSTGRES_DB}'
engine_auth_sync = create_engine(DATABASE_AUTH_URL_SYNC, pool_pre_ping=True)
SessionLocalAuthSync = sessionmaker(autocommit=False, autoflush=False, bind=engine_auth_sync)

DATABASE_NOTIFICATIONS_URL_SYNC = (f'postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@'
                                   f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}')
engine_sync = create_engine(DATABASE_NOTIFICATIONS_URL_SYNC, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_sync)

Base = declarative_base()
