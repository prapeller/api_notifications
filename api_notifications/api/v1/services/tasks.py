import fastapi as fa

from core.dependencies import sqlalchemy_repo_sync_dependency
from core.enums import ResponseDetailEnum
from db.models.celery_tasks import PeriodicTaskModel
from db.repository_sync import SqlAlchemyRepositorySync
from db.serializers.celery_tasks import (
    PeriodicTaskReadSchedulesSerializer,
    PeriodicTaskCreateSchedulesSerializer,
    PeriodicTaskUpdateSchedulesSerializer,
)
from services.notificator.message_preparer import validate_placeholders

router = fa.APIRouter()


@router.get("/periodic-tasks/{task_id}", response_model=PeriodicTaskReadSchedulesSerializer)
async def celery_periodic_tasks_read(
        task_id: str,
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    tasks = repo.get(PeriodicTaskModel, id=task_id)
    return tasks


@router.get("/periodic-tasks", response_model=list[PeriodicTaskReadSchedulesSerializer])
async def celery_periodic_tasks_list(
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    tasks = repo.get_all(PeriodicTaskModel)
    return tasks


@router.post("/periodic-tasks", response_model=PeriodicTaskReadSchedulesSerializer)
async def celery_periodic_tasks_create(
        periodic_task_ser: PeriodicTaskCreateSchedulesSerializer,
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    msg_text = await periodic_task_ser.get_msg_text_async()
    await validate_placeholders(msg_text)
    task = repo.create_periodic_task_with_schedule(periodic_task_ser)
    return task


@router.put("/periodic-tasks/{task_id}", response_model=PeriodicTaskReadSchedulesSerializer)
async def celery_periodic_tasks_update(
        task_id: int,
        periodic_task_ser: PeriodicTaskUpdateSchedulesSerializer,
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    msg_text = await periodic_task_ser.get_msg_text_async()
    await validate_placeholders(msg_text)
    task = repo.get(PeriodicTaskModel, id=task_id)
    task = repo.update_periodic_task_with_schedule(task, periodic_task_ser)
    return task


@router.delete("/periodic-tasks/{task_id}")
async def celery_periodic_tasks_delete(
        task_id: int,
        repo: SqlAlchemyRepositorySync = fa.Depends(sqlalchemy_repo_sync_dependency),
):
    task = repo.get(PeriodicTaskModel, id=task_id)
    repo.update(task, {'enabled': False})
    return {'detail': ResponseDetailEnum.ok}
