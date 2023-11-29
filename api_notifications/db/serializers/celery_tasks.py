import datetime as dt
import json
import re

import pydantic as pd

from core.enums import TaskPriorityEnum, PeriodEnum, NotificatorCeleryTasksEnum
from core.exceptions import BadRequestException


class IntervalScheduleUpdateSerializer(pd.BaseModel):
    every: int | None = None
    period: PeriodEnum | None = None


class IntervalScheduleCreateSerializer(IntervalScheduleUpdateSerializer):
    every: int
    period: PeriodEnum


class IntervalScheduleReadSerializer(IntervalScheduleCreateSerializer):
    id: int
    every: int
    period: PeriodEnum


class CrontabScheduleUpdateSerializer(pd.BaseModel):
    minute: str | None = None
    hour: str | None = None
    day_of_week: str | None = None
    day_of_month: str | None = None
    month_of_year: str | None = None
    timezone: str | None = 'UTC'

    @pd.field_validator('minute')
    @classmethod
    def validate_minute(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([0-5]?\d)([-/][0-5]?\d)*)+(,(\*|([0-5]?\d)([-/][0-5]?\d)*))*$', v):
            raise ValueError("Invalid minute format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('hour')
    @classmethod
    def validate_hour(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([01]?\d|2[0-3])([-/][01]?\d|2[0-3])*)+(,(\*|([01]?\d|2[0-3])([-/][01]?\d|2[0-3])*))*$', v):
            raise ValueError("Invalid hour format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v: str):
        if v is not None and v != '' and not re.match(r'^(\*|([0-6])([-/][0-6])*)+(,(\*|([0-6])([-/][0-6])*))*$', v):
            raise ValueError("Invalid day_of_week format. Valid formats: '*', '1', '1-5', '1,3,5', '*/2'")
        return v

    @pd.field_validator('day_of_month')
    @classmethod
    def validate_day_of_month(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([1-9]|[12]\d|3[01])([-/][1-9]|[12]\d|3[01])*)'
                r'+(,(\*|([1-9]|[12]\d|3[01])([-/][1-9]|[12]\d|3[01])*))*$', v):
            raise ValueError("Invalid day_of_month format. Valid formats: '*', '5', '10-20', '5,10,15', '*/5'")
        return v

    @pd.field_validator('month_of_year')
    @classmethod
    def validate_month_of_year(cls, v: str):
        if v is not None and v != '' and not re.match(
                r'^(\*|([1-9]|1[0-2])([-/][1-9]|1[0-2])*)+(,(\*|([1-9]|1[0-2])([-/][1-9]|1[0-2])*))*$', v):
            raise ValueError("Invalid month_of_year format. Valid formats: '*', '1', '1-12', '1,6,12', '*/3'")
        return v


class CrontabScheduleCreateSerializer(CrontabScheduleUpdateSerializer):
    minute: str | None = None
    hour: str | None = None
    day_of_week: str | None = None
    day_of_month: str | None = None
    month_of_year: str | None = None
    timezone: str | None = None


class CrontabScheduleReadSerializer(CrontabScheduleCreateSerializer):
    id: int


class PeriodicTaskUpdateSerializer(pd.BaseModel):
    name: str | None = None
    task: NotificatorCeleryTasksEnum | None = None
    interval_id: int | None = None
    crontab_id: int | None = None
    args: str | None = '[]'
    kwargs: str | None = '{}'
    queue: str | None = 'default'
    priority: TaskPriorityEnum | None = TaskPriorityEnum.mass_message_for_all_users_task_priority
    description: str | None = ''
    enabled: bool | None = True
    start_time: dt.datetime | None = None
    expires: dt.datetime | None = None

    class Config:
        from_attributes = True

    async def get_msg_text_async(self):
        return json.loads(self.kwargs).get('msg_text')

    def get_msg_text(self):
        return json.loads(self.kwargs).get('msg_text')

    def get_email_to(self):
        return json.loads(self.kwargs).get('email_to')

    def get_user_uuid(self):
        return json.loads(self.kwargs).get('user_uuid')

    def get_user_uuid_list(self):
        return json.loads(self.kwargs).get('user_uuid_list')

    def __init__(self, **data):
        super().__init__(**data)
        # if updating for disable/enable - no any fields validation needed
        if self.task is None:
            return

        # if task is 'check pending messages' - no other fields validation needed
        if self.task == NotificatorCeleryTasksEnum.check_availability_and_notify_pending_messages_all_task:
            self.priority = TaskPriorityEnum.check_pending_messages_task_priority
            return

        # for other tasks - 'message' is needed
        msg_text = self.get_msg_text()
        if msg_text is None or msg_text == '':
            raise BadRequestException('msg_text must be provided')

        # and 'addressee' is needed
        if self.task == NotificatorCeleryTasksEnum.send_email_task:
            email_to = self.get_email_to()
            if email_to is None or email_to == '':
                raise BadRequestException('email_to must be provided')
            self.priority = TaskPriorityEnum.email_task_priority
        elif self.task == NotificatorCeleryTasksEnum.send_individual_immediate_message_task:
            user_uuid = self.get_user_uuid()
            if user_uuid is None or user_uuid == '':
                raise BadRequestException('user_uuid must be provided')
            self.priority = TaskPriorityEnum.individual_immediate_message_task_priority
        elif self.task == NotificatorCeleryTasksEnum.send_individual_pending_message_task:
            user_uuid = self.get_user_uuid()
            if user_uuid is None or user_uuid == '':
                raise BadRequestException('user_uuid must be provided')
            self.priority = TaskPriorityEnum.individual_pending_message_task_priority
        elif self.task == NotificatorCeleryTasksEnum.send_mass_message_to_filtered_users_task:
            user_uuid_list = self.get_user_uuid_list()
            if user_uuid_list is None or user_uuid_list == []:
                raise BadRequestException('user_uuid_list must be provided')
            self.priority = TaskPriorityEnum.mass_message_for_filtered_users_task_priority
        elif self.task == NotificatorCeleryTasksEnum.send_mass_message_to_all_users_task:
            self.priority = TaskPriorityEnum.mass_message_for_all_users_task_priority


class PeriodicTaskCreateSerializer(PeriodicTaskUpdateSerializer):
    name: str
    task: NotificatorCeleryTasksEnum

    class Config:
        from_attributes = True


class PeriodicTaskReadSerializer(PeriodicTaskCreateSerializer):
    id: int
    description: str
    date_changed: dt.datetime | None = None
    total_run_count: int
    last_run_at: dt.datetime | None = None
    one_off: bool

    class Config:
        from_attributes = True


class PeriodicTaskUpdateSchedulesSerializer(PeriodicTaskUpdateSerializer):
    interval: IntervalScheduleUpdateSerializer | None = None
    crontab: CrontabScheduleUpdateSerializer | None = None

    class Config:
        from_attributes = True


class PeriodicTaskCreateSchedulesSerializer(PeriodicTaskCreateSerializer):
    interval: IntervalScheduleCreateSerializer | None = None
    crontab: CrontabScheduleUpdateSerializer | None = None

    class Config:
        from_attributes = True


class PeriodicTaskReadSchedulesSerializer(PeriodicTaskReadSerializer):
    interval: IntervalScheduleReadSerializer | None = None
    crontab: CrontabScheduleReadSerializer | None = None

    class Config:
        from_attributes = True


PeriodicTaskUpdateSchedulesSerializer.model_rebuild()
PeriodicTaskCreateSchedulesSerializer.model_rebuild()
PeriodicTaskReadSchedulesSerializer.model_rebuild()
