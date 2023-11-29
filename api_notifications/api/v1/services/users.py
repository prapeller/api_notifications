import fastapi as fa
import pydantic as pd

from core.dependencies import sqlalchemy_repo_async_dependency
from db.repository_async import SqlAlchemyRepositoryAsync
from db.serializers.user import UserReadSerializer

router = fa.APIRouter()


@router.post("/duplicate-user", response_model=UserReadSerializer)
async def users_duplicate(
        user_uuid: pd.UUID4 = fa.Body(...),
        user_email: pd.EmailStr = fa.Body(...),
        repo: SqlAlchemyRepositoryAsync = fa.Depends(sqlalchemy_repo_async_dependency),
):
    return await repo.get_or_create_duplicated_user(user_uuid, user_email)
