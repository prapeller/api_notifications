import fastapi as fa
import pydantic as pd

from core.dependencies import (
    current_user_dependency,
    sqlalchemy_repo_sync_dependency,
)
from core.exceptions import UnauthorizedException
from db.models.message import MessageModel
from db.models.user import UserModel
from db.repository_sync import SqlAlchemyRepositorySync
from db.serializers.message import MessageReadSerializer, MessageUpdateSerializer

router = fa.APIRouter()


@router.get("/to-me",
            response_model=list[MessageReadSerializer]
            )
async def messages_list_all_to_me(
        current_user: UserModel = fa.Depends(current_user_dependency),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    get messages sent to current user
    """
    return await repo.get(MessageModel, to_user_uuid=current_user.uuid, is_notified=True)


@router.get("/{message_uuid}",
            response_model=MessageReadSerializer
            )
async def messages_read(
        message_uuid: pd.UUID4 = fa.Path(...),
        current_user: UserModel = fa.Depends(current_user_dependency),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    get message by uuid
    """
    message = repo.get(MessageModel, uuid=message_uuid.hex)
    if message.to_user_uuid != current_user.uuid:
        raise UnauthorizedException

    return message


@router.put("/mark-read-many",
            response_model=list[MessageReadSerializer]
            )
async def messages_update_mark_read_many(
        message_uuid_list: list[pd.UUID4] = fa.Body(...),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    set to messages from message_id_list 'is_read'=True
    """
    messages = repo.get_many_by_uuid_list(MessageModel, message_uuid_list)
    repo.update_many(messages, {'is_read': True})
    return messages


@router.put("/{message_uuid}",
            response_model=MessageReadSerializer
            )
async def messages_update(
        message_uuid: pd.UUID4 = fa.Path(...),
        message_ser: MessageUpdateSerializer = fa.Body(...),
        current_user: UserModel = fa.Depends(current_user_dependency),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    update message by uuid
    """
    message = repo.get(MessageModel, uuid=message_uuid)
    message = repo.update(message, message_ser)
    return message


@router.delete("/many")
async def messages_delete_many(
        message_uuid_list: list[pd.UUID4] = fa.Body(...),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    delete many messages from id_list
    """
    repo.remove_many_by_uuid_list(MessageModel, message_uuid_list)
    return {'message': 'ok'}


@router.delete("/{message_id}")
async def messages_delete(
        message_uuid: pd.UUID4 = fa.Path(...),
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    """
    delete message
    """
    repo.remove(MessageModel, message_uuid)
    return {'message': 'ok'}
