from contextlib import asynccontextmanager

import fastapi as fa
import uvicorn
from fastapi.responses import ORJSONResponse

from api.v1.auth import messages as v1_auth_messages
from api.v1.auth import postgres as v1_auth_postgres
from api.v1.auth import users as v1_auth_users
from api.v1.services import notifications as v1_services_notifications
from api.v1.services import tasks as v1_services_tasks
from api.v1.services import users as v1_services_users
from core.config import settings
from core.dependencies import verified_access_token_dependency, verify_service_secret_dependency
from db import init_models


@asynccontextmanager
async def lifespan(app: fa.FastAPI):
    init_models()
    # startup
    yield
    # shutdown


app = fa.FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=f'/{settings.DOCS_URL}',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

v1_router_auth = fa.APIRouter(
    dependencies=[fa.Depends(verified_access_token_dependency)],
)
v1_router_auth.include_router(v1_auth_messages.router, prefix='/messages', tags=['messages'])
v1_router_auth.include_router(v1_auth_postgres.router, prefix='/postgres', tags=['postgres'])
v1_router_auth.include_router(v1_auth_users.router, prefix='/users', tags=['users'])

v1_router_services = fa.APIRouter(dependencies=[fa.Depends(verify_service_secret_dependency)])
v1_router_services.include_router(v1_services_notifications.router, prefix='/services-notifications',
                                  tags=['services-notifications'])
v1_router_services.include_router(v1_services_tasks.router, prefix='/services-tasks',
                                  tags=['services-tasks'])
v1_router_services.include_router(v1_services_users.router, prefix='/services-users',
                                  tags=['services-users'])

app.include_router(v1_router_auth, prefix="/api/v1")
app.include_router(v1_router_services, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run('main:app', host=settings.API_NOTIFICATIONS_HOST, port=settings.API_NOTIFICATIONS_PORT, reload=True)
