import datetime as dt

import sqlalchemy as sa
from celery.utils.log import get_logger
from sqlalchemy.event import listen
from sqlalchemy.orm import relationship

from db import Base
from db.models._shared import Identified

logger = get_logger('celery_sqlalchemy_scheduler.models')


def cronexp(field_value):
    return field_value if field_value not in ('', None) else '-'


class IntervalScheduleModel(Identified, Base):
    __tablename__ = 'celery_interval_schedule'

    every = sa.Column(sa.Integer, nullable=False)
    period = sa.Column(sa.String(24))

    periodic_tasks = relationship("PeriodicTaskModel",
                                  back_populates='interval',
                                  primaryjoin='PeriodicTaskModel.interval_id==IntervalScheduleModel.id')

    __table_args__ = (
        sa.UniqueConstraint('every', 'period', name='uq_every_period'),
    )

    def __repr__(self):
        return f'{self.every=:} {self.period}'


class CrontabScheduleModel(Identified, Base):
    __tablename__ = 'celery_crontab_schedule'

    minute = sa.Column(sa.String(60 * 4))
    hour = sa.Column(sa.String(24 * 4))
    day_of_week = sa.Column(sa.String(64))
    day_of_month = sa.Column(sa.String(31 * 4))
    month_of_year = sa.Column(sa.String(64))
    timezone = sa.Column(sa.String(64), server_default=sa.text("'UTC'"))

    periodic_tasks = relationship("PeriodicTaskModel",
                                  back_populates='crontab',
                                  primaryjoin='PeriodicTaskModel.crontab_id==CrontabScheduleModel.id')

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY) {5}'.format(
            cronexp(self.minute), cronexp(self.hour),
            cronexp(self.day_of_week), cronexp(self.day_of_month),
            cronexp(self.month_of_year), cronexp(str(self.timezone))
        )

    def __repr__(self):
        return str(self)


class SolarScheduleModel(Identified, Base):
    __tablename__ = 'celery_solar_schedule'

    event = sa.Column(sa.String(24))
    latitude = sa.Column(sa.Float())
    longitude = sa.Column(sa.Float())

    periodic_tasks = relationship("PeriodicTaskModel",
                                  back_populates='solar',
                                  primaryjoin='PeriodicTaskModel.solar_id==SolarScheduleModel.id')

    def __repr__(self):
        return f'{self.event=:}, {self.latitude=:}, {self.longitude}'


class PeriodicTaskModel(Identified, Base):
    __tablename__ = 'celery_periodic_task'

    name = sa.Column(sa.String(255), unique=True)
    task = sa.Column(sa.String(255))

    interval_id = sa.Column(sa.Integer, sa.ForeignKey('celery_interval_schedule.id'))
    interval = relationship(
        'IntervalScheduleModel',
        back_populates='periodic_tasks',
        uselist=False,
        primaryjoin='PeriodicTaskModel.interval_id==IntervalScheduleModel.id',
        post_update=True,
    )

    crontab_id = sa.Column(sa.Integer, sa.ForeignKey('celery_crontab_schedule.id'))
    crontab = relationship(
        'CrontabScheduleModel',
        back_populates='periodic_tasks',
        uselist=False,
        primaryjoin='PeriodicTaskModel.crontab_id==CrontabScheduleModel.id',
    )

    solar_id = sa.Column(sa.Integer, sa.ForeignKey('celery_solar_schedule.id'))
    solar = relationship(
        'SolarScheduleModel',
        back_populates='periodic_tasks',
        uselist=False,
        primaryjoin='PeriodicTaskModel.solar_id==SolarScheduleModel.id',
    )

    args = sa.Column(sa.Text(), server_default=sa.text("'[]'"))
    kwargs = sa.Column(sa.Text(), server_default=sa.text("'{}'"))
    queue = sa.Column(sa.String(255))
    exchange = sa.Column(sa.String(255))
    routing_key = sa.Column(sa.String(255))
    priority = sa.Column(sa.Integer())
    expires = sa.Column(sa.DateTime(timezone=True))

    one_off = sa.Column(sa.Boolean(), server_default=sa.text("false"))
    start_time = sa.Column(sa.DateTime(timezone=True))
    enabled = sa.Column(sa.Boolean(), server_default=sa.text("true"))
    last_run_at = sa.Column(sa.DateTime(timezone=True))
    total_run_count = sa.Column(sa.Integer(), nullable=False, default=0)
    date_changed = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(),
                             onupdate=sa.func.current_timestamp())
    description = sa.Column(sa.Text(), server_default=sa.text("''"))

    def __repr__(self):
        fmt = '{0.name}: {0.task} {{no schedule}}'
        if self.interval:
            fmt = '{0.name}: {0.task} {0.interval}'
        elif self.crontab:
            fmt = '{0.name}: {0.task} {0.crontab}'
        elif self.solar:
            fmt = '{0.name}: {0.task} {0.solar}'
        return fmt.format(self)


class PeriodicTaskChangedModel(Identified, Base):
    """Helper table for tracking updates to periodic tasks."""

    __tablename__ = 'celery_periodic_task_changed'

    last_update = sa.Column(sa.DateTime(timezone=True), nullable=False, onupdate=sa.func.current_timestamp())

    @classmethod
    def update_changed(cls, mapper, connection, target):
        s = connection.execute(sa.select(PeriodicTaskChangedModel).where(PeriodicTaskChangedModel.id == 1).limit(1))
        if not s:
            s = connection.execute(sa.insert(PeriodicTaskChangedModel), last_update=dt.datetime.now())
        else:
            s = connection.execute(sa.update(PeriodicTaskChangedModel).where(PeriodicTaskChangedModel.id == 1)
                                   .values(last_update=dt.datetime.now()))


listen(PeriodicTaskModel, 'after_insert', PeriodicTaskChangedModel.update_changed)
listen(PeriodicTaskModel, 'after_delete', PeriodicTaskChangedModel.update_changed)
listen(PeriodicTaskModel, 'after_update', PeriodicTaskChangedModel.update_changed)
listen(IntervalScheduleModel, 'after_insert', PeriodicTaskChangedModel.update_changed)
listen(IntervalScheduleModel, 'after_delete', PeriodicTaskChangedModel.update_changed)
listen(IntervalScheduleModel, 'after_update', PeriodicTaskChangedModel.update_changed)
listen(CrontabScheduleModel, 'after_insert', PeriodicTaskChangedModel.update_changed)
listen(CrontabScheduleModel, 'after_delete', PeriodicTaskChangedModel.update_changed)
listen(CrontabScheduleModel, 'after_update', PeriodicTaskChangedModel.update_changed)
listen(SolarScheduleModel, 'after_insert', PeriodicTaskChangedModel.update_changed)
listen(SolarScheduleModel, 'after_delete', PeriodicTaskChangedModel.update_changed)
listen(SolarScheduleModel, 'after_update', PeriodicTaskChangedModel.update_changed)
