import datetime as dt

import pydantic as pd

from core.enums import UTCTimeZonesEnum
from db.serializers.message import MessageReadSerializer


class UserMeUpdateSerializer(pd.BaseModel):
    timezone: UTCTimeZonesEnum | None = None

    is_accepting_emails: bool | None = None
    is_accepting_interface_messages: bool | None = None
    is_accepting_telegram: bool | None = None
    telegram_id: str | None = None


class UserUpdateSerializer(pd.BaseModel):
    email: pd.EmailStr | None = None
    timezone: UTCTimeZonesEnum | None = None

    is_accepting_emails: bool | None = None
    is_accepting_interface_messages: bool | None = None
    telegram_id: str | None = None
    is_accepting_telegram: bool | None = None

    def __eq__(self, other):
        return self.email == other.email


class UserCreateSerializer(UserUpdateSerializer):
    uuid: str
    email: pd.EmailStr


class UserReadSerializer(UserCreateSerializer):
    id: int
    updated_at: dt.datetime | None = None
    created_at: dt.datetime


class UserReadMessagesSerializer(UserReadSerializer):
    accepted_messages: list[MessageReadSerializer] = []

    class Config:
        from_attributes = True
