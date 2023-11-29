import sqlalchemy as sa


class Identified:
    id = sa.Column(sa.Integer, primary_key=True)


class IdentifiedCreatedUpdated(Identified):
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.current_timestamp(), nullable=True)
