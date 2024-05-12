from enum import Enum
from os import environ
from pathlib import Path
from typing import Callable


def load_env(path: Path | None = None) -> dict[str, str]:
    if path is None:
        path = Path.cwd() / ".env"
    with path.open("r") as f:
        env = {line.split("=")[0]: line.split("=")[1].strip() for line in f.readlines()}
    environ.update(env)
    return env


def set_default(
    target: object, attr: str, default_type: Callable, default_value: object = None
) -> object:
    if hasattr(target, attr):
        setattr(target, attr, default_type(getattr(target, attr)))
        return getattr(target, attr)
    setattr(target, attr, default_value)
    return default_value


class HttpStatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    UNKNOWN = -1
