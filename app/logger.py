import logging
import sys
import json
from typing import Any, Callable, Dict

from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s %(event)s"
)
logger.addHandler(stream_handler)
stream_handler.setFormatter(log_formatter)


class LoggingAPIRoute(APIRoute):
    """
    `APIRouter` route_class add class event: Dict
    logger.info('request', extra={"event": event})
    logger.info('response', extra={"event": event})

    ## Example

    ```python
    from fastapi import APIRouter, FastAPI
    from logger import LoggingAPIRoute

    app = FastAPI()
    router = APIRouter(route_class=LoggingAPIRoute)


    @router.get("/users/", tags=["users"])
    async def read_users():
        return [{"username": "Rick"}, {"username": "Morty"}]


    app.include_router(router)
    ```
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            await self._request_log(request)
            response: Response = await original_route_handler(request)
            self._response_log(request, response)
            return response

        return custom_route_handler

    @staticmethod
    def _has_json_body(request: Request) -> bool:
        if (
            request.method in ("POST", "PUT", "PATCH")
            and request.headers.get("content-type") == "application/json"
        ):
            return True
        return False

    async def _request_log(self, request: Request) -> None:
        event: Dict[str, Any] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "headers": request.headers,
            "queryParams": request.query_params,
        }

        if self._has_json_body(request):
            request_body = await request.body()
            event["body"] = request_body.decode("UTF-8")

        logger.info("request", extra={"event": event})

    @staticmethod
    def _response_log(request: Request, response: Response) -> None:
        event: Dict[str, str] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "status_code": response.status_code,
            "body": response.body.decode("UTF-8"),
        }

        logger.info("response", extra={"event": event})
