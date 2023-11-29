import datetime as dt
import smtplib
from email.message import EmailMessage

import fastapi as fa
import httpx
import pydantic as pd
import pytz
from core import config
from core.config import settings
from core.enums import MessagePriorityEnum
from core.timezones import TIMEZONES_DICT
from db.models.message import MessageModel
from db.models.user import UserModel
from db.repository_sync import SqlAlchemyRepositorySync
from db.serializers.message import MessageCreateSerializer
from services.notificator.logger_config import logger
from services.notificator.message_preparer import render_message_text_with_auth_user_data


class Notificator:

    def __init__(self, repo: SqlAlchemyRepositorySync | None = None):
        self.repo = repo

    async def send_email(self,
                         email_to: pd.EmailStr,
                         msg_text: str,
                         msg_subject: str = "Notification from cinema.online",
                         msg_from: pd.EmailStr = settings.EMAILS_FROM_EMAIL,
                         ):
        try:
            msg_text += "\nThis email was sent automatically, you don't need to reply to it.\n" \
                        "To cancel receiving - visit cinema.online settings and turn off email notifications."""
            msg = EmailMessage()
            msg['Subject'] = msg_subject
            msg['From'] = msg_from
            msg['To'] = email_to
            msg.set_content(msg_text)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.send_message(msg)
            logger.debug(f"email sending success to {email_to=:}")
        except Exception as e:
            logger.error(f"email sending failed to {email_to=:}: {e}")

    async def send_email_to_user(self,
                                 user: UserModel,
                                 msg_text: str,
                                 msg_subject: str = "Notification from cinema.online",
                                 msg_from: pd.EmailStr = settings.EMAILS_FROM_EMAIL) -> None:
        if user.is_accepting_emails:
            await self.send_email(user.email, msg_text, msg_subject, msg_from)

    async def send_telegram_to_user(self,
                                    user: UserModel,
                                    msg_text: str) -> None:
        """sends message to user.telegram_id using telegram api"""
        if user.is_accepting_telegram and user.telegram_id:
            try:
                msg_text += "\nMore information at cinema.online."
                data = {"chat_id": user.telegram_id, "text": msg_text}
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url=f"https://api.telegram.org/{settings.TG_BOT_ID}/sendMessage",
                                             data=data)
                    if resp.status_code == fa.status.HTTP_200_OK:
                        logger.debug(f"telegram sending success to {user=:}.")
                    else:
                        logger.error(f"telegram sending failed to {user=:}. {resp.status_code=:}, {resp.text=:}")
            except (httpx._exceptions.RequestError, httpx._exceptions.HTTPError) as e:
                logger.error(f"telegram sending failed to {user=:}: {e}")

    async def notify_interface_message_to_user(self, user: UserModel, message: MessageModel) -> None:
        if user.is_accepting_interface_messages:
            self.repo.update(message, {'is_notified': True})
            logger.debug(f"interface_message success notified to {user=:}.")

    async def create_and_notify_interface_message_to_user(self, user: UserModel, msg_text: str) -> None:
        """if user is accepting interface message: creates it and notifies it immediately"""
        if user.is_accepting_interface_messages:
            self.repo.create(MessageModel,
                             MessageCreateSerializer(to_user_uuid=user.uuid,
                                                     text=msg_text,
                                                     priority=MessagePriorityEnum.individual_immediate,
                                                     is_notified=True))
            logger.debug(f"interface_message success created and notified to {user=:}.")

    async def send_individual_immediate_message(self, user_uuid, msg_text):
        """send messages to all communication ways immediately"""
        msg_text = render_message_text_with_auth_user_data(user_uuid, msg_text)

        user = self.repo.get(UserModel, uuid=user_uuid)
        await self.send_email_to_user(user, msg_text)
        await self.send_telegram_to_user(user, msg_text)
        await self.create_and_notify_interface_message_to_user(user, msg_text)

    async def send_individual_pending_message(self, user_uuid: str, msg_text: str,
                                              priority=MessagePriorityEnum.individual_pending, user=None):
        """firstly create message as 'pending' (is_notified=False), and
            -if users current_time.hour is in users 'available_hours' - send it immediately
            -else message stays pending and scheduled sender will send it when user timezone allows it"""
        msg_text = render_message_text_with_auth_user_data(user_uuid, msg_text)
        message = self.repo.create(MessageModel,
                                   MessageCreateSerializer(to_user_uuid=user_uuid,
                                                           text=msg_text,
                                                           priority=priority,
                                                           is_notified=False))
        if user is None:
            user = self.repo.get(UserModel, uuid=user_uuid)
        user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[user.timezone]))
        if user_current_time.hour in config.USER_NOTIFICATION_AVAILABLE_HOURS:
            await self.send_email_to_user(user, msg_text)
            await self.send_telegram_to_user(user, msg_text)
            await self.notify_interface_message_to_user(user, message)

    async def send_mass_message_to_user_uuid_list(self, user_uuid_list: list[str], msg_text: str):
        """create pending messages for filtered users"""
        for user_uuid in user_uuid_list:
            await self.send_individual_pending_message(user_uuid=user_uuid, msg_text=msg_text,
                                                       priority=MessagePriorityEnum.mass_filtered_users)

    async def send_mass_message_to_all_users(self, msg_text: str):
        """create pending messages for all users"""
        for user in self.repo.get_all(UserModel):
            await self.send_individual_pending_message(user_uuid=user.uuid, msg_text=msg_text,
                                                       priority=MessagePriorityEnum.mass_all_users,
                                                       user=user)

    async def check_availability_and_notify_pending_messages_by_uuid_list(self, pending_messages_uuids: list[str]):
        """check users timezone availability and notify message"""
        for message_uuid in pending_messages_uuids:
            message = self.repo.get(MessageModel, uuid=message_uuid)
            user_current_time = dt.datetime.now(pytz.timezone(TIMEZONES_DICT[message.to_user.timezone]))
            if user_current_time.hour in config.USER_NOTIFICATION_AVAILABLE_HOURS:
                await self.send_email_to_user(message.to_user, message.text)
                await self.send_telegram_to_user(message.to_user, message.text)
                await self.notify_interface_message_to_user(message.to_user, message)
