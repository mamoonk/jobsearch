import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.error")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                "Unhandled error: %s\n%s",
                str(e),
                "".join(traceback.format_exc()),
                extra={"path": request.url.path, "method": request.method},
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "path": request.url.path},
            )
