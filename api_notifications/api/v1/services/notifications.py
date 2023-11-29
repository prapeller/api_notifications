import fastapi as fa
import pydantic as pd

from core.enums import ResponseDetailEnum, TaskPriorityEnum
from db import SessionLocal
from db.repository_sync import SqlAlchemyRepositorySync
from services.notificator.celery_tasks import (
    send_email_task,
    send_individual_immediate_message_task,
    send_individual_pending_message_task,
    send_mass_message_to_filtered_users_task,
    send_mass_message_to_all_users_task,
)
from services.notificator.message_preparer import validate_placeholders
from services.notificator.notificator import Notificator

router = fa.APIRouter()


@router.post("/send-email")
async def notifications_send_email(
        email_to: pd.EmailStr = fa.Body(...),
        msg_text: str = fa.Body(...),
        as_celery_task: bool | None = fa.Query(default=False),
):
    if as_celery_task:
        task = send_email_task.apply_async(
            kwargs={'email_to': email_to, 'msg_text': msg_text},
            priority=TaskPriorityEnum.email_task_priority,
            queue='default')
        return {'detail': ResponseDetailEnum.ok, 'task_id': f'{task.task_id}'}

    notificator = Notificator(repo=None)
    await notificator.send_email(email_to, msg_text)
    return {'detail': ResponseDetailEnum.ok}


@router.post("/send-individual-immediate-message")
async def notifications_send_individual_immediate_message(
        user_uuid: pd.UUID4 = fa.Body(...),
        msg_text: str = fa.Body(...),
        as_celery_task: bool | None = fa.Query(default=False),
):
    await validate_placeholders(msg_text)

    if as_celery_task:
        task = send_individual_immediate_message_task.apply_async(
            kwargs={'user_uuid': user_uuid.hex, 'msg_text': msg_text},
            priority=TaskPriorityEnum.individual_immediate_message_task_priority,
            queue='default')
        return {'detail': ResponseDetailEnum.ok, 'task_id': f'{task.task_id}'}

    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    await notificator.send_individual_immediate_message(user_uuid.hex, msg_text)
    repo.session.close()
    return {'detail': ResponseDetailEnum.ok}


@router.post("/send-individual-pending-message")
async def notifications_send_individual_pending_message(
        user_uuid: pd.UUID4 = fa.Body(...),
        msg_text: str = fa.Body(...),
        as_celery_task: bool | None = fa.Query(default=False),
):
    await validate_placeholders(msg_text)

    if as_celery_task:
        task = send_individual_pending_message_task.apply_async(
            kwargs={'user_uuid': user_uuid.hex, 'msg_text': msg_text},
            priority=TaskPriorityEnum.individual_pending_message_task_priority,
            queue='default')
        return {'detail': ResponseDetailEnum.ok, 'task_id': f'{task.task_id}'}

    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    await notificator.send_individual_pending_message(user_uuid.hex, msg_text)
    repo.session.close()
    return {'detail': ResponseDetailEnum.ok}


@router.post("/send-mass-message-to-filtered-users")
async def notifications_send_mass_message_to_filtered_users(
        user_uuid_list: list[pd.UUID4] = fa.Body(...),
        msg_text: str = fa.Body(...),
        as_celery_task: bool | None = fa.Query(default=True),
):
    await validate_placeholders(msg_text)

    user_uuid_list = [_uuid.hex for _uuid in user_uuid_list]
    if as_celery_task:
        task = send_mass_message_to_filtered_users_task.apply_async(
            kwargs={'user_uuid_list': user_uuid_list, 'msg_text': msg_text},
            priority=TaskPriorityEnum.mass_message_for_filtered_users_task_priority,
            queue='default')
        return {'detail': ResponseDetailEnum.ok, 'task_id': f'{task.task_id}'}

    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    await notificator.send_mass_message_to_user_uuid_list(user_uuid_list, msg_text)
    repo.session.close()
    return {'detail': ResponseDetailEnum.ok}


@router.post("/send-mass-message-to-all-users")
async def notifications_send_mass_message_to_all_users(
        msg_text: str = fa.Body(...),
        as_celery_task: bool | None = fa.Query(default=True),
):
    await validate_placeholders(msg_text)

    if as_celery_task:
        task = send_mass_message_to_all_users_task.apply_async(
            kwargs={'msg_text': msg_text},
            priority=TaskPriorityEnum.mass_message_for_all_users_task_priority,
            queue='default')
        return {'detail': ResponseDetailEnum.ok, 'task_id': f'{task.task_id}'}

    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    await notificator.send_mass_message_to_all_users(msg_text)
    repo.session.close()
    return {'detail': ResponseDetailEnum.ok}
