import sqlalchemy as sa
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import IdentifiedCreatedUpdated


class MessageModel(IdentifiedCreatedUpdated, Base):
    __tablename__ = 'message'
    uuid = sa.Column(sa.UUID(as_uuid=False), server_default=sa.text("uuid_generate_v4()"),
                     unique=True, index=True, nullable=False)

    theme = sa.Column(sa.String)
    text = sa.Column(sa.Text)
    is_read = sa.Column(sa.Boolean, default=False)
    priority = sa.Column(sa.Integer, index=True)
    is_notified = sa.Column(sa.Boolean, default=False)

    to_user_uuid = sa.Column(sa.UUID(as_uuid=False), sa.ForeignKey('user.uuid'))
    to_user = relationship("UserModel",
                           back_populates='accepted_messages',
                           primaryjoin='UserModel.uuid==MessageModel.to_user_uuid',
                           post_update=True)

    def __repr__(self):
        return f"<MessageModel> ({self.id=:}, {self.uuid=:}, {self.to_user_uuid=:}, {self.theme=:})"
