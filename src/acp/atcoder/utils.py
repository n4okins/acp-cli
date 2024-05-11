import sys
from enum import Enum


def force_input(prompt: str) -> str:
    x = input(prompt)
    while True:
        try:
            if x:
                return x
            x = input(prompt)
        except KeyboardInterrupt:
            print("Interrupted. Exiting...")
            sys.exit(1)
        except EOFError:
            print("EOF. Exiting...")
            sys.exit(1)


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
