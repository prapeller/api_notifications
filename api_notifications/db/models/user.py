import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated
from db.models.message import MessageModel


class UserModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'user'
    uuid = sa.Column(sa.UUID(as_uuid=False), unique=True, index=True, nullable=False)

    email = sa.Column(sa.String(50), unique=True, index=True)
    timezone = sa.Column(sa.String(10), nullable=False, server_default=sa.text("'UTC+3'::character varying"))

    is_accepting_emails = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))
    is_accepting_interface_messages = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('true'))
    telegram_id = sa.Column(sa.String(255))
    is_accepting_telegram = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('false'))

    accepted_messages = relationship("MessageModel",
                                     back_populates='to_user',
                                     primaryjoin='MessageModel.to_user_uuid==UserModel.uuid')

    @hybrid_property
    def pending_messages(self):
        return [message for message in self.accepted_messages if not message.is_notified]

    @pending_messages.expression
    def pending_messages(cls):
        return sa.select(MessageModel).where(
            sa.and_(MessageModel.to_user_uuid == cls.uuid, MessageModel.is_notified == False))

    def __repr__(self):
        return f'<UserModel> ({self.id=:}, {self.uuid=:},{self.email=:})'
