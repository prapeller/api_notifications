import abc
from typing import Type

import fastapi as fa
import pydantic as pd
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as pd_Model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.query import Query

from db import Base as sa_Model
from db.models.celery_tasks import IntervalScheduleModel, PeriodicTaskModel, CrontabScheduleModel
from db.serializers.celery_tasks import (
    PeriodicTaskCreateSchedulesSerializer,
    PeriodicTaskCreateSerializer,
    PeriodicTaskUpdateSchedulesSerializer,
    PeriodicTaskUpdateSerializer,
)


class AbstractRepositorySync(abc.ABC):
    @abc.abstractmethod
    def create(self, Model, serializer):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, Model, **kwargs) -> sa_Model:
        raise NotImplementedError


class SqlAlchemyRepositorySync(AbstractRepositorySync):
    def __init__(self, session):
        self.session = session

    def create(self, Model: Type[sa_Model], serializer: pd_Model) -> sa_Model:
        serializer_data = jsonable_encoder(serializer)
        obj = Model(**serializer_data)
        self.session.add(obj)
        try:
            self.session.commit()
            self.session.refresh(obj)
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)
        return obj

    def get(self, Model: Type[sa_Model], **kwargs) -> sa_Model:
        obj = self.session.query(Model).filter_by(**kwargs).first()
        if obj is None:
            raise fa.HTTPException(status_code=404, detail=f"{Model} not found")
        return obj

    def get_many_by_id_list(self, Model: Type[sa_Model], id_list: list[int]) -> list[sa_Model]:
        """getting objs one by one and if cant find any of them, raises 404"""
        objs = []
        for id in id_list:
            obj = self.session.query(Model).get(id)
            if obj is None:
                raise fa.HTTPException(status_code=404,
                                       detail=f"Trying to get {Model} with id {id}, which is not found.")
            objs.append(obj)
        return objs

    def get_many_by_uuid_list(self, Model: Type[sa_Model], uuid_list: list[pd.UUID4]) -> list[sa_Model]:
        """getting objs one by one and if cant find any of them, raises 404"""
        objs = []
        for _uuid in uuid_list:
            obj = self.get(Model, uuid=_uuid.hex)
            if obj is None:
                raise fa.HTTPException(status_code=404,
                                       detail=f"Trying to get {Model} with uuid {_uuid.hex}, which is not found.")
            objs.append(obj)
        return objs

    def get_all(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).all()

    def get_all_active(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).filter(Model.is_active == True).all()

    def get_all_inactive(self, Model: Type[sa_Model]) -> list[sa_Model]:
        return self.session.query(Model).filter(Model.is_active == False).all()

    def get_query(self, Model: Type[sa_Model], **kwargs) -> Query:
        query = self.session.query(Model)
        for attr, value in kwargs.items():
            query = query.filter(Model.__dict__.get(attr) == value)
        return query

    def get_query_all_active(self, Model: Type[sa_Model], **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=True, **kwargs)

    def get_query_all_inactive(self, Model: Type[sa_Model], **kwargs) -> Query:
        return self.session.query(Model).filter_by(is_active=False, **kwargs)

    def get_or_create(self, Model: Type[sa_Model], serializer: pd_Model) -> tuple[bool, sa_Model]:
        serializer_data = jsonable_encoder(serializer)
        is_created = False
        obj = self.session.query(Model).filter_by(**serializer_data).first()
        if obj is None:
            obj = Model(**serializer_data)
            self.session.add(obj)
            try:
                self.session.commit()
                # refresh db-generated values like .created_at/.timezone etc. (which specified as 'server_default')
                self.session.refresh(obj)
                is_created = True
            except IntegrityError as e:
                self.session.rollback()
                raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                       detail=e.orig.diag.message_detail)
        return is_created, obj

    def create_many(self, Model: Type[sa_Model], serializers: list[pd_Model]) -> list[sa_Model]:
        objs = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            obj = Model(**serializer_data)
            self.session.add(obj)
            objs.append(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=e.orig.diag.message_detail)
        return objs

    def get_or_create_many(self, Model: Type[sa_Model], serializers: list[pd_Model]) -> list[sa_Model]:
        objs = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            obj = self.session.query(Model).filter_by(**serializer_data).first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=e.orig.diag.message_detail)
        return objs

    def get_or_create_by_name(self, Model: Type[sa_Model], name: str) -> sa_Model:
        obj = self.session.query(Model).filter_by(name=name).first()
        if not obj:
            obj = Model(name=name)
            self.session.add(obj)
            try:
                self.session.commit()
                self.session.refresh(obj)
            except IntegrityError as e:
                self.session.rollback()
                fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail=e.orig.diag.message_detail)
        return obj

    def get_or_create_by_kwargs(self, Model: Type[sa_Model], **kwargs) -> tuple[bool, sa_Model]:
        is_created = False
        obj = self.session.query(Model).filter_by(**kwargs).first()
        if not obj:
            obj = Model(**kwargs)
            self.session.add(obj)
            try:
                self.session.commit()
                self.session.refresh(obj)
                is_created = True
            except IntegrityError as e:
                self.session.rollback()
                fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                 detail=e.orig.diag.message_detail)
        return is_created, obj

    def update(self, obj: sa_Model, serializer: pd_Model | dict) -> sa_Model:
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.model_dump(exclude_unset=True, exclude_none=True)

        # explicitly remove (set as None)
        #   - interval/crontab if None provided as foreign keys of those,
        #   - expires/start_time if None provided as their values
        if isinstance(serializer, PeriodicTaskUpdateSerializer):
            if serializer.interval_id is None:
                update_data['interval_id'] = None
            if serializer.crontab_id is None:
                update_data['crontab_id'] = None
            if serializer.expires is None:
                update_data['expires'] = None
            if serializer.start_time is None:
                update_data['start_time'] = None

        fields_to_update = [x for x in update_data if hasattr(obj, x)]
        for field in fields_to_update:
            setattr(obj, field, update_data[field])

        self.session.add(obj)
        try:
            self.session.commit()
            self.session.refresh(obj)
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)
        return obj

    def update_many(self, objs: list[sa_Model], serializer: pd_Model | dict) -> list[sa_Model]:
        # assert objects_are_the_same_type(objs), 'all objects must be the same type'
        update_data = serializer if isinstance(serializer, dict) else serializer.dict(exclude_unset=True)

        for obj in objs:
            fields_to_update = [x for x in update_data if hasattr(obj, x)]
            for field in fields_to_update:
                setattr(obj, field, update_data[field])
            self.session.add(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)

        return objs

    def remove(self, Model: Type[sa_Model], id: int) -> None:
        obj = self.session.query(Model).get(id)
        if obj is None:
            raise fa.HTTPException(status_code=404,
                                   detail=f"Trying to remove {Model} with id {id}, which is not found.")
        self.session.delete(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)

    def remove_by_uuid(self, Model: Type[sa_Model], _uuid: pd.UUID4) -> None:
        obj = self.get(Model, uuid=_uuid.hex)
        if obj is None:
            raise fa.HTTPException(status_code=404,
                                   detail=f"Trying to remove {Model} with uuid {_uuid.hex}, which is not found.")
        self.session.delete(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)

    def remove_many_by_id_list(self, Model: Type[sa_Model], id_list: list[int]) -> None:
        """remove objects if found them"""
        objs = self.session.query(Model).filter(Model.id.in_(id_list)).all()
        for obj in objs:
            self.session.delete(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)

    def remove_many_by_uuid_list(self, Model: Type[sa_Model], uuid_list: list[pd.UUID4]) -> None:
        """remove objects if found them"""
        objs = self.session.query(Model).filter(Model.uuid.in_([_uuid.hex for _uuid in uuid_list])).all()
        for obj in objs:
            self.session.delete(obj)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise fa.HTTPException(status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   detail=e.orig.diag.message_detail)

    def create_periodic_task_with_schedule(
            self,
            periodic_task_ser: PeriodicTaskCreateSchedulesSerializer) -> PeriodicTaskModel:
        if periodic_task_ser.interval is not None:
            is_created, interval = self.get_or_create(IntervalScheduleModel, periodic_task_ser.interval)
            periodic_task_ser.interval_id = interval.id

        if periodic_task_ser.crontab is not None:
            is_created, crontab = self.get_or_create(CrontabScheduleModel, periodic_task_ser.crontab)
            periodic_task_ser.crontab_id = crontab.id

        periodic_task = self.create(PeriodicTaskModel,
                                    PeriodicTaskCreateSerializer(**periodic_task_ser.model_dump()))
        return periodic_task

    def update_periodic_task_with_schedule(
            self,
            periodic_task: PeriodicTaskModel,
            periodic_task_ser: PeriodicTaskUpdateSchedulesSerializer) -> PeriodicTaskModel:
        if periodic_task_ser.interval is not None:
            periodic_task_ser.crontab_id = None
            is_created, interval = self.get_or_create(
                IntervalScheduleModel, periodic_task_ser.interval)
            periodic_task_ser.interval_id = interval.id

        if periodic_task_ser.crontab is not None:
            periodic_task_ser.interval_id = None
            is_created, crontab = self.get_or_create(
                CrontabScheduleModel, periodic_task_ser.crontab)
            periodic_task_ser.crontab_id = crontab.id
        periodic_task = self.update(periodic_task, PeriodicTaskUpdateSerializer(**periodic_task_ser.model_dump()))
        return periodic_task
