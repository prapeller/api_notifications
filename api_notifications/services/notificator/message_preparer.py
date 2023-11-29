import re

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError

from core.enums import UserDataRenderPlaceholdersEnum, ResponseDetailEnum
from core.exceptions import NotValidPlaceholdersException, AuthPostgresConnectionException
from db import SessionLocalAuthSync
from services.notificator.logger_config import logger


async def validate_placeholders(msg_text: str):
    if msg_text:
        placeholders = re.findall(r'%\w+%', msg_text)
        if placeholders:
            not_valid = []
            for placeholder in placeholders:
                if placeholder not in [p.value for p in UserDataRenderPlaceholdersEnum]:
                    not_valid.append(placeholder)
            if not_valid:
                detail = f"{ResponseDetailEnum.not_valid_placeholders} {not_valid}"
                raise NotValidPlaceholdersException(detail)


def render_message_text_with_auth_user_data(user_uuid: str, msg_text: str):
    placeholders = re.findall(r'%\w+%', msg_text)
    if placeholders:
        session = SessionLocalAuthSync()
        try:
            user_data_cur = session.execute(sa.text(f"select u.name from public.user u where uuid='{user_uuid}'"))
            user_data = user_data_cur.first()
        except SQLAlchemyError as e:
            detail = f'failed render_message_text_with_auth_user_data: {user_uuid=:} {e}'
            logger.error(detail)
            raise AuthPostgresConnectionException(str(e))
        finally:
            session.close()
        for p in placeholders:
            if p == UserDataRenderPlaceholdersEnum.user_name:
                msg_text = msg_text.replace(p, user_data[0])
    return msg_text
