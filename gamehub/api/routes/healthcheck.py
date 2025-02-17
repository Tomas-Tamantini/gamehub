from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import Response

healthcheck_router = APIRouter(prefix="/health", tags=["health"])


@healthcheck_router.get("/", status_code=HTTPStatus.NO_CONTENT.value)
def health_check():
    return Response(status_code=HTTPStatus.NO_CONTENT)
