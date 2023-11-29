import abc

import pydantic as pd
import sqlalchemy.ext.asyncio as sa_async
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from core.exceptions import BadRequestException
from db import Base as sa_BaseModel
from db.models.user import UserModel
from db.serializers.user import UserCreateSerializer, UserUpdateSerializer


class AbstractRepositoryAsync(abc.ABC):
    @abc.abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def remove(self, *args, **kwargs):
        pass


class SqlAlchemyRepositoryAsync(AbstractRepositoryAsync):
    def __init__(self, session: sa_async.AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def create(self, Model: type[sa_BaseModel], serializer) -> sa_BaseModel:
        serializer_data = jsonable_encoder(serializer)
        obj = Model(**serializer_data)
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')

        await self.session.refresh(obj)
        return obj

    async def get(self, Model: type[sa_BaseModel], **kwargs) -> sa_BaseModel:
        stmt = select(Model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        return obj

    async def get_all(self, Model: type[sa_BaseModel]) -> list[sa_BaseModel]:
        stmt = select(Model)
        result = await self.session.execute(stmt)
        objs = result.scalars().all()
        return objs

    async def get_or_create_many(
            self, Model: type[sa_BaseModel], serializers: list[pd.BaseModel]
    ) -> list[sa_BaseModel]:
        objs = []
        for serializer in serializers:
            serializer_data = jsonable_encoder(serializer)
            stmt = select(Model).filter_by(**serializer_data)
            result = await self.session.execute(stmt)
            obj = result.scalars().first()
            if obj is None:
                obj = Model(**serializer_data)
                self.session.add(obj)
            objs.append(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while creating {Model=:}: {str(e)}')
        return objs

    async def get_or_create_by_name(self, Model: type[sa_BaseModel], name: str) -> tuple[bool, sa_BaseModel]:
        is_created = False
        stmt = select(Model).filter_by(name=name)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if not obj:
            obj = Model(name=name)
            self.session.add(obj)
            try:
                await self.session.commit()
            except IntegrityError as e:
                await self.session.rollback()
                raise ValueError(f'Error while creating {Model=:}: {str(e)}')
            await self.session.refresh(obj)
            is_created = True
        return is_created, obj

    async def get_or_create(self, Model: type[sa_BaseModel], serializer: pd.BaseModel) -> tuple[bool, sa_BaseModel]:
        is_created = False
        stmt = select(Model).filter_by(**serializer.model_dump())
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        if not obj:
            obj = Model(**serializer.model_dump())
            self.session.add(obj)
            try:
                await self.session.commit()
            except IntegrityError as e:
                await self.session.rollback()
                raise ValueError(f'Error while creating {Model=:}: {str(e)}')
            await self.session.refresh(obj)
            is_created = True
        return is_created, obj

    async def update(self, obj: sa_BaseModel, serializer: pd.BaseModel | dict) -> sa_BaseModel:
        if isinstance(serializer, dict):
            update_data = serializer
        else:
            update_data = serializer.model_dump(exclude_unset=True)

        # Filter out fields that should not be updated
        fields_to_update = [x for x in update_data if hasattr(obj, x)]
        for field in fields_to_update:
            setattr(obj, field, update_data[field])
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while updating {obj=:}: {str(e)}')
        await self.session.refresh(obj)
        return obj

    async def remove(self, Model: type[sa_BaseModel], id) -> None:
        obj = await self.get(Model, id=id)
        if obj is None:
            raise BadRequestException(f'Cant remove, {Model=:} {id=:} not found')
        await self.session.delete(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f'Error while removing {Model=:} {id=:}: {str(e)}')

    async def get_or_create_duplicated_user(self,
                                            current_user_uuid: pd.UUID4,
                                            current_user_email: pd.EmailStr) -> UserModel:
        user = await self.get(UserModel, uuid=current_user_uuid)

        if user is None:
            user = await self.create(UserModel, UserCreateSerializer(uuid=current_user_uuid.hex, email=current_user_email))
        elif user is not None and current_user_email != user.email:
            user = await self.update(user, UserUpdateSerializer(email=current_user_email))
        return user
