import logging
import uuid
from enum import Enum

import pydantic as pd
from bson import ObjectId


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', 'None')
        return True


def custom_dumps(obj: pd.BaseModel | dict) -> dict:
    if isinstance(obj, pd.BaseModel):
        obj = obj.model_dump()
    for key, value in obj.items():
        if isinstance(value, uuid.UUID):
            obj[key] = str(value)
        elif isinstance(value, ObjectId):
            obj[key] = str(value)
        elif isinstance(value, Enum):
            obj[key] = str(value)
        elif isinstance(value, list):
            for v in value:
                v = custom_dumps(v)
    return obj


def user_likes_dumps(obj: pd.BaseModel | dict) -> dict:
    if isinstance(obj, pd.BaseModel):
        obj = obj.model_dump()
    for key, value in obj.items():
        if isinstance(value, uuid.UUID):
            obj[key] = str(value)
        elif isinstance(value, ObjectId):
            obj[key] = str(value)
    return obj
