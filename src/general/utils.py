from os import environ
from pathlib import Path


def load_env(path: Path | None = None) -> dict[str, str]:
    if path is None:
        path = Path.cwd() / ".env"
    with path.open("r") as f:
        env = {line.split("=")[0]: line.split("=")[1].strip() for line in f.readlines()}
    environ.update(env)
    return env
