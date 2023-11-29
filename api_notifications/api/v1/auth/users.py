import fastapi as fa

from core.dependencies import current_user_dependency, sqlalchemy_repo_async_dependency
from db.repository_async import SqlAlchemyRepositoryAsync
from db.serializers.user import UserReadSerializer, UserMeUpdateSerializer

router = fa.APIRouter()


@router.put("/me", response_model=UserReadSerializer)
async def users_update_me(
        user_ser: UserMeUpdateSerializer,
        current_user=fa.Depends(current_user_dependency),
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
):
    return await repo.update(current_user, user_ser)
