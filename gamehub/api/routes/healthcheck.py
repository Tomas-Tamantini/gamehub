from http import HTTPStatus

from fastapi import APIRouter

healthcheck_router = APIRouter(prefix="/health", tags=["health"])


@healthcheck_router.get("/", status_code=HTTPStatus.OK.value)
def health_check():
    return {"status": "ok"}
