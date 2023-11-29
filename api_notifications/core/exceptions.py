import fastapi as fa

from core.enums import ResponseDetailEnum


class BadRequestException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=ResponseDetailEnum.bad_request if detail is None else detail,
        )


class AuthPostgresConnectionException(fa.HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=fa.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ResponseDetailEnum.auth_postgres_error if detail is None else detail,
        )


class NotValidPlaceholdersException(fa.HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=fa.status.HTTP_400_BAD_REQUEST,
            detail=ResponseDetailEnum.not_valid_placeholders if detail is None else detail,
        )


class UnauthorizedException(fa.HTTPException):
    def __init__(self, detail=None):
        super().__init__(
            status_code=fa.status.HTTP_401_UNAUTHORIZED,
            detail=ResponseDetailEnum.unauthorized if detail is None else detail,
        )
