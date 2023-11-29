import datetime as dt

import pydantic as pd

from core.enums import MessagePriorityEnum


class MessageUpdateSerializer(pd.BaseModel):
    theme: str | None = None
    text: str | None = None
    is_read: bool | None = None
    is_notified: bool | None = None

    to_user_uuid: str | None = None

    class Config:
        from_attributes = True


class MessageCreateSerializer(MessageUpdateSerializer):
    to_user_uuid: str
    text: str
    is_notified: bool = False
    priority: MessagePriorityEnum = MessagePriorityEnum.mass_all_users

    class Config:
        from_attributes = True


class MessageReadSerializer(MessageCreateSerializer):
    id: int
    uuid: str
    created_at: dt.datetime
    updated_at: dt.datetime | None = None

    class Config:
        from_attributes = True
