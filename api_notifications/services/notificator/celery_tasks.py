import asyncio

from celery_app import celery_app
from core.enums import MessagePriorityEnum, TaskPriorityEnum
from db import SessionLocal
from db.models.message import MessageModel
from db.repository_sync import SqlAlchemyRepositorySync
from services.notificator.logger_config import logger
from services.notificator.notificator import Notificator


# PRIORITY 1
@celery_app.task(name='send_email_task')
def send_email_task(email_to, msg_text):
    logger.debug('send_email_task started')
    notificator = Notificator(repo=None)  # as far as repo not needed for just sending email...
    asyncio.run(notificator.send_email(email_to=email_to, msg_text=msg_text))


# PRIORITY 2
@celery_app.task(name='send_individual_immediate_message_task')
def send_individual_immediate_message_task(user_uuid: str, msg_text: str):
    logger.debug(f'send_individual_immediate_message_task started: {user_uuid=:}')
    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    asyncio.run(notificator.send_individual_immediate_message(user_uuid, msg_text))
    repo.session.close()


# PRIORITY 3
@celery_app.task(name='send_individual_pending_message_task')
def send_individual_pending_message_task(user_uuid: str, msg_text: str):
    logger.debug('send_individual_pending_message_task started')
    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    asyncio.run(notificator.send_individual_pending_message(user_uuid, msg_text))
    repo.session.close()


# PRIORITY 4
@celery_app.task(name='check_availability_and_notify_pending_messages_by_uuid_list_task')
def check_availability_and_notify_pending_messages_by_uuid_list_task(message_uuid_list):
    logger.debug(f'check_availability_and_notify_pending_messages_by_uuid_list_task started: {message_uuid_list=:}')
    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    asyncio.run(notificator.check_availability_and_notify_pending_messages_by_uuid_list(message_uuid_list))
    repo.session.close()


@celery_app.task(name='check_availability_and_notify_pending_messages_all_task')
def check_availability_and_notify_pending_messages_all_task():
    logger.debug('check_availability_and_notify_pending_messages_all_task started')
    repo = SqlAlchemyRepositorySync(SessionLocal())

    message_individual_pending = repo.get_query(MessageModel,
                                                is_notified=False,
                                                priority=MessagePriorityEnum.individual_pending).all()
    messages_mass_filtered_users = repo.get_query(MessageModel,
                                                  is_notified=False,
                                                  priority=MessagePriorityEnum.mass_filtered_users).all()
    messages_mass_all_users = repo.get_query(MessageModel,
                                             is_notified=False,
                                             priority=MessagePriorityEnum.mass_all_users).all()

    if message_individual_pending:
        check_availability_and_notify_pending_messages_by_uuid_list_task.apply_async(
            args=([message.uuid for message in message_individual_pending],),
            priority=TaskPriorityEnum.individual_pending_message_task_priority,
            queue='default')
    if messages_mass_filtered_users:
        check_availability_and_notify_pending_messages_by_uuid_list_task.apply_async(
            args=([message.uuid for message in messages_mass_filtered_users],),
            priority=TaskPriorityEnum.mass_message_for_filtered_users_task_priority,
            queue='default')
    if messages_mass_all_users:
        check_availability_and_notify_pending_messages_by_uuid_list_task.apply_async(
            args=([message.uuid for message in messages_mass_all_users],),
            priority=TaskPriorityEnum.mass_message_for_all_users_task_priority,
            queue='default')
    repo.session.close()


# PRIORITY 5
@celery_app.task(name='send_mass_message_to_filtered_users_task')
def send_mass_message_to_filtered_users_task(user_uuid_list: list[str], msg_text: str):
    logger.debug('send_mass_message_for_filtered_users_task started')
    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    asyncio.run(notificator.send_mass_message_to_user_uuid_list(user_uuid_list, msg_text))
    repo.session.close()


# PRIORITY 6
@celery_app.task(name='send_mass_message_to_all_users_task')
def send_mass_message_to_all_users_task(msg_text: str):
    logger.debug('send_mass_message_to_all_users_task started')
    repo = SqlAlchemyRepositorySync(SessionLocal())
    notificator = Notificator(repo)
    asyncio.run(notificator.send_mass_message_to_all_users(msg_text))
    repo.session.close()
