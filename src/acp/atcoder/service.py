from abc import ABC, abstractmethod
from logging import getLogger

import bs4
import requests
from bs4 import BeautifulSoup

from .utils import HttpStatusCode

logger = getLogger(__name__)


class WebService(ABC):
    class URLs:
        pass

    class Exceptions:
        class AccessError(Exception):
            pass

        class LoginFailedError(Exception):
            pass

    def __init__(self) -> None:
        self._session: requests.Session = requests.Session()

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def is_logged_in(self) -> bool:
        return False

    def get(self, url: str, *args: tuple, **kwargs: dict) -> BeautifulSoup:
        logger.info("GET: %s", url)
        res = self._session.get(url, *args, **kwargs)
        if res.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to get {url}. Status code: {res.status_code}"
            raise self.Exceptions.AccessError(msg)
        return BeautifulSoup(res.text, "html.parser")

    def post(self, url: str, *args: tuple, **kwargs: dict) -> BeautifulSoup:
        logger.info("POST: %s", url)
        res = self._session.post(url, *args, **kwargs)
        if res.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to post {url}. Status code: {res.status_code}"
            raise self.Exceptions.AccessError(msg)
        return BeautifulSoup(res.text, "html.parser")

    @abstractmethod
    def login(self, data: dict) -> None:
        pass

    def get_cookies(self) -> None:
        for cookie in self._session.cookies:
            print(cookie)


class AtCoder(WebService):
    class URLs(WebService.URLs):
        BASE = "https://atcoder.jp"
        LOGIN = f"{BASE}/login"

    class AtCoderExceptions(WebService.Exceptions):
        pass

    def __init__(self) -> None:
        super().__init__()

    def login(self, username: str, password: str) -> None:
        if self.is_logged_in:
            return
        res = self.get(self.URLs.LOGIN)
        form = res.find("form", action="")
        if not isinstance(form, bs4.Tag):
            msg = "Failed to get login form."
            raise self.AtCoderExceptions.LoginFailedError(msg)
        print(form.find_all("input"))
        # res = self.post(self.URLs.LOGIN, data=data)
        # print(res)
