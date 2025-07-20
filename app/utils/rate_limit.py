from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


from fastapi import Request, Depends
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def rate_limit_dependency(request: Request):
    limiter = request.app.state.limiter
    key = get_remote_address(request)
    route = request.scope.get("path")
    if not limiter:
        return
    try:
        limiter.limit("5/minute")(lambda request: None)(request)  # 5 запитів за хвилину
    except RateLimitExceeded as exc:
        raise exc
