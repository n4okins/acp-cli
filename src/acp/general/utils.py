import os
from enum import Enum
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def load_env(path: Path | None = None) -> dict[str, str]:
    """
    .envファイルを読み込んで環境変数に設定する

    Args:
        path (Path | None, optional): .envファイルのパス. Defaults to None.

    Returns:
        dict[str, str]: .envから読み込んだ環境変数
    """
    if path is None:
        path = Path.cwd() / ".env"
    if not path.exists():
        # カレントディレクトリに.envがなければ親ディレクトリを探索
        for p in Path.cwd().parents:
            if (p / ".env").exists():
                # .envファイルが見つかったらそれを読み込む
                path = p / ".env"
                break
    logger.info(f"Load environment variables from {path}")
    if not path.exists():
        logger.warning(f"{path} does not exist.")
        return {}

    with path.open("r") as f:
        # .envファイルを読み込んで環境変数に設定
        # 例: KEY=VALUE
        env = {line.split("=")[0]: line.split("=")[1].strip() for line in f.readlines()}
    os.environ.update(env)  # 環境変数を更新
    return env  # .envの内容を返す


def add_gitignore(items: list[str], root: Path | None = None) -> None:
    root = root or Path.cwd()
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        for p in root.parents:
            gitignore = p / ".gitignore"
            if gitignore.exists():
                break
        else:
            gitignore = root / ".gitignore"

    newfile = False
    if not gitignore.exists():
        newfile = True
        gitignore.touch()

    with gitignore.open("r") as f:
        for item in f:
            item = item.strip()
            if item in items:
                del items[items.index(item)]

    if items:
        print(f"Automatically add the following items {items} to {gitignore}")
        with gitignore.open("a") as f:
            f.write(("" if newfile else "\n") + "\n".join(items))


class HttpStatusCode(Enum):
    """
    HTTPステータスコード
    """

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


def color(r: int, g: int, b: int) -> str:
    """
    ターミナルに色を付けるためのANSIエスケープシーケンスを生成する

    Args:
        r (int): 赤成分 0-255
        g (int): 緑成分 0-255
        b (int): 青成分 0-255
    """
    return f"\033[38;2;{r};{g};{b}m"


def bg_color(r: int, g: int, b: int) -> str:
    """
    ターミナルに背景色を付けるためのANSIエスケープシーケンスを生成する

    Args:
        r (int): 赤成分 0-255
        g (int): 緑成分 0-255
        b (int): 青成分 0-255
    """
    return f"\033[48;2;{r};{g};{b}m"


def reset_color() -> str:
    """
    ターミナルの色をリセットするためのANSIエスケープシーケンスを生成する
    """
    return "\033[0m"


def confirm_yn_input(msg: str = "") -> bool:
    """
    ユーザーにy/nで確認する

    Args:
        msg (str, optional): メッセージ. Defaults to "".

    Returns:
        y/YならTrue, n/NならFalse
    """
    x = input(msg)
    while True:
        try:
            if x in ["y", "Y"]:
                return True
            elif x in ["n", "N"]:
                return False
            else:
                x = input(msg)

        except Exception as e:
            print(e)
            return False
