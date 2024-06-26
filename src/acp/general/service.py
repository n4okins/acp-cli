import pickle
import time
from logging import getLogger
from pathlib import Path
from typing import Any

import requests
import requests.cookies
from bs4 import BeautifulSoup

from acp.general.utils import HttpStatusCode

logger = getLogger(__name__)


class WebService:
    """
    Webサービスにアクセスしてアレコレするための基底クラス
    """

    class URLs:
        pass

    class Exceptions:
        class AccessError(Exception):
            pass

        class LoginFailedError(Exception):
            pass

        class ProblemsNotFoundError(Exception):
            pass

    def __init__(self, parser: str = "lxml", session_dir: Path | None = None) -> None:
        self._session: requests.Session = requests.Session()
        self._response: requests.Response | None = None
        self._soup: BeautifulSoup | None = None
        self._session_dir = session_dir or (Path.cwd() / ".session")
        self.parser = parser
        self._session_dir.mkdir(parents=True, exist_ok=True)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def is_logged_in(self) -> bool:
        return False

    @property
    def response(self) -> requests.Response:
        return self._response if self._response else requests.Response()

    @property
    def soup(self) -> BeautifulSoup:
        return self._soup if self._soup else BeautifulSoup()

    def get(
        self, url: str, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> BeautifulSoup:
        """
        getメソッド
        requests.getを実行し、BeautifulSoupオブジェクトを返す
        self._soupにBeautifulSoupオブジェクトを格納して、
        self._responseにrequests.Responseオブジェクトを格納する

        Args:
            url (str): URL
            *args (tuple): requests.getの引数
            **kwargs (dict): requests.getのキーワード引数

        Returns:
            BeautifulSoup: BeautifulSoupオブジェクト
        """

        logger.info("GET: %s", url)
        self._response = self._session.get(url, *args, **kwargs)  # type: ignore
        self.wait(0.25)
        if self.response.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to get {url}. Status code: {self.response.status_code}"
            raise self.Exceptions.AccessError(msg)
        self._soup = BeautifulSoup(self.response.text, self.parser)
        return self.soup

    def post(
        self, url: str, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> BeautifulSoup:
        """
        postメソッド
        requests.postを実行し、BeautifulSoupオブジェクトを返す
        self._soupにBeautifulSoupオブジェクトを格納して、
        self._responseにrequests.Responseオブジェクトを格納する

        Args:
            url (str): URL
            *args (tuple): requests.postの引数
            **kwargs (dict): requests.postのキーワード引数

        Returns:
            BeautifulSoup: BeautifulSoupオブジェクト
        """
        logger.info("POST: %s", url)
        self._response = self._session.post(url, *args, **kwargs)  # type: ignore
        if self.response.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to post {url}. Status code: {self.response.status_code}"
            raise self.Exceptions.AccessError(msg)
        self._soup = BeautifulSoup(self.response.text, self.parser)
        return self.soup

    def login(self, data: dict[Any, Any]) -> None:
        """
        ログイン処理とか
        """
        pass

    @property
    def cookies(self) -> requests.cookies.RequestsCookieJar:
        return self._session.cookies

    def save_session(self, file_path: Path | None = None) -> None:
        file_path = file_path or (self._session_dir / "websession")
        with file_path.open("wb") as f:
            pickle.dump(self.cookies, f)

    def load_session(self, file_path: Path | None = None) -> None:
        file_path = file_path or (self._session_dir / "websession")
        if file_path.exists():
            with file_path.open("rb") as f:
                self.cookies.update(pickle.load(f))
