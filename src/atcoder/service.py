import os
import re
import time
import weakref
from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path

import bs4
import requests
import requests.cookies
from bs4 import BeautifulSoup

from src.atcoder.judge import JudgeResult, JudgeRunner
from src.atcoder.models import AtCoderContest, AtCoderProblem
from src.general.utils import HttpStatusCode, bg_color, color, reset_color

logger = getLogger(__name__)


class WebService(ABC):
    class URLs:
        pass

    class Exceptions:
        class AccessError(Exception):
            pass

        class LoginFailedError(Exception):
            pass

        class ProblemsNotFoundError(Exception):
            pass

    def __init__(self, parser: str = "lxml") -> None:
        self._session: requests.Session = requests.Session()
        self._response: requests.Response | None = None
        self._soup: BeautifulSoup | None = None
        self.parser = parser

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

    def get(self, url: str, *args: tuple, **kwargs: dict) -> BeautifulSoup:
        logger.info("GET: %s", url)
        self._response = self._session.get(url, *args, **kwargs)
        if self.response.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to get {url}. Status code: {self.response.status_code}"
            raise self.Exceptions.AccessError(msg)
        self._soup = BeautifulSoup(self.response.text, self.parser)
        return self.soup

    def post(self, url: str, *args: tuple, **kwargs: dict) -> BeautifulSoup:
        logger.info("POST: %s", url)
        self._response = self._session.post(url, *args, **kwargs)
        if self.response.status_code != HttpStatusCode.OK.value:
            msg = f"Failed to post {url}. Status code: {self.response.status_code}"
            raise self.Exceptions.AccessError(msg)
        self._soup = BeautifulSoup(self.response.text, self.parser)
        return self.soup

    @abstractmethod
    def login(self, data: dict) -> None:
        pass

    @property
    def cookies(self) -> requests.cookies.RequestsCookieJar:
        return self._session.cookies


class AtCoder(WebService):
    _cache: dict = {}

    class URLs(WebService.URLs):
        BASE = "https://atcoder.jp"
        LOGIN = f"{BASE}/login"
        SETTINGS = f"{BASE}/settings"

    class AtCoderExceptions(WebService.Exceptions):
        pass

    def __init__(self) -> None:
        super().__init__()

    def get(
        self,
        url: str,
        params: dict = {},
        headers: dict = {},
        *args: tuple,
        use_cache: bool = True,
        **kwargs: dict,
    ) -> BeautifulSoup:
        if use_cache and url in self._cache:
            self._response = self._cache[url]["response"]
            self._soup = self._cache[url]["soup"]
            return self.soup
        params.update({"lang": "ja"})
        super().get(url, *args, params=params, headers=headers, **kwargs)
        self._cache[url] = {"response": self.response, "soup": self.soup}
        return self.soup

    def post(
        self,
        url: str,
        params: dict = {},
        headers: dict = {},
        *args: tuple,
        **kwargs: dict,
    ) -> BeautifulSoup:
        params.update({"lang": "ja"})
        return super().post(url, *args, params=params, headers=headers, **kwargs)

    @property
    def alerts(self) -> dict[str, list[str]]:
        alerts = {
            "success": [],
            "info": [],
            "warning": [],
            "danger": [],
        }
        for alert in self.soup.find_all("div", class_="alert"):
            alerts[alert.attrs.get("class")[1].split("-")[1]].append(alert.text.strip())
        return alerts

    @property
    def is_logged_in(self) -> bool:
        return self._session.get(self.URLs.SETTINGS).url == self.URLs.SETTINGS

    def login(self, username: str, password: str) -> None:
        if self.is_logged_in:
            return
        logger.info("Logging in...")
        logger.info("Username: %s", username)
        logger.info("Password: %s", "*" * len(password))
        res = self.get(self.URLs.LOGIN, use_cache=False)
        self.wait(0.5)
        form: bs4.Tag = res.find("form", action="")  # type: ignore

        *_, csrf_token = form.find_all("input")
        data = {
            "username": username,
            "password": password,
            "csrf_token": csrf_token["value"],
        }
        self.post(
            self.URLs.LOGIN,
            data=data,
        )
        self.wait(0.5)
        if self.alerts["danger"]:
            raise self.AtCoderExceptions.LoginFailedError(self.alerts["danger"])
        elif self.alerts["warning"]:
            logger.warning("Alerts: %s", self.alerts["warning"])
        elif self.alerts["info"]:
            logger.info("Alerts: %s", self.alerts["info"])
        elif self.alerts["success"]:
            logger.info("Alerts: %s", self.alerts["success"])

    def get_contest(self, contest: str, use_cache: bool = True) -> AtCoderContest:
        contest = (
            contest
            if f"{self.URLs.BASE}/contests/" in contest
            else f"{self.URLs.BASE}/contests/{contest}"
        )
        c = AtCoderContest(name=contest.split("/")[-1], url=contest)
        self.get(c.url, use_cache=use_cache)
        table = self.soup.find("table", class_="table")
        if table is None:
            msg = f"Problems not found in {c.url}. Is the contest name correct?"
            raise self.AtCoderExceptions.ProblemsNotFoundError(msg)
        t = list(filter(lambda x: x, table.text.split("\n")))
        points = {t[i]: int(t[i + 1]) for i in range(2, len(t), 2)}
        c.points = points
        for problem_id in points.keys():
            c.problems[problem_id] = self.get_problem(
                difficulty=problem_id,
                url=f"{c.url}/tasks/{c.name}_{problem_id.lower()}",
                contest=weakref.proxy(c),
                point=points[problem_id],
            )
        return c

    def get_problem(
        self,
        url: str,
        *,
        difficulty: str = "",
        contest: AtCoderContest | None = None,
        point: int = 0,
    ) -> AtCoderProblem:
        problem = AtCoderProblem(
            difficulty=difficulty,
            url=url,
            contest=contest or AtCoderContest(name="", url=""),
            point=point,
        )
        self.get(problem.url)
        self.wait(0.25)
        title = self.soup.find("span", class_="h2")
        if title is None:
            msg = f"Title not found in {problem.url}. Is the problem ID correct?"
            raise self.AtCoderExceptions.ProblemsNotFoundError(msg)
        problem.title = title.text.strip().split("\n")[0].split(" - ")[1]
        problem.name = problem.url.split("/")[-1]
        return problem

    def download_problem(
        self, problem: AtCoderProblem, target_dir: str | Path | None = None
    ) -> None:
        target_dir = (
            Path(target_dir)
            if target_dir
            else (Path.cwd() / problem.contest.name / problem.name.lower())
        )

        (target_dir / "in").mkdir(exist_ok=True, parents=True)
        (target_dir / "out").mkdir(exist_ok=True, parents=True)

        self.get(problem.url)
        self.wait(0.25)

        # Parse problem statement
        sample = re.compile(r"<h3>[入出]力例 \d+</h3><pre>([^<]+)[\n\r]</pre>").findall(
            str(self.soup)
        )
        sample = [s.strip() for s in sample]
        for i in range(0, len(sample), 2):
            with (
                (target_dir / "in" / f"sample-{i // 2}.in").open("w") as in_f,
                (target_dir / "out" / f"sample-{i // 2}.out").open("w") as out_f,
            ):
                in_f.write(sample[i] + "\n")
                out_f.write(sample[i + 1] + "\n")

    def download_contest(self, contest: AtCoderContest):
        for problem in contest.problems.values():
            self.download_problem(problem)

    def test(
        self,
        problem: AtCoderProblem,
        *,
        target_dir: Path | str | None = None,
        command: list[str] = ["python", "main.py"],
    ):
        target_dir = (
            Path(target_dir)
            if isinstance(target_dir, str)
            else target_dir
            or (Path.cwd() / problem.contest.name / problem.name.lower())
        )

        runner = JudgeRunner(command=command, cd=target_dir)
        lines = []
        lines.append(
            bg_color(32, 32, 32)
            + color(255, 255, 255)
            + "-" * 16
            + " "
            + problem.name
            + " "
            + "-" * 16
            + reset_color()
        )
        colormap = {
            JudgeResult.AC: color(64, 255, 64),  # Green
            JudgeResult.WA: color(255, 64, 64),  # Red
            JudgeResult.RE: color(255, 255, 64),  # Yellow
            JudgeResult.TLE: color(255, 192, 128),  # Orange
            JudgeResult.IE: color(64, 255, 255),  # Cyan
        }
        for i in range(len(list((target_dir / "in").iterdir()))):
            code, meta = runner(
                target_dir / "in" / f"sample-{i}.in",
                target_dir / "out" / f"sample-{i}.out",
            )
            line = (
                bg_color(32, 32, 32)
                + color(255, 255, 255)
                + f" sample-{i} "
                + reset_color()
                + color(255, 255, 255)
                + bg_color(32, 32, 32)
                + "["
                + colormap[code]
                + f" {code.value} "
                + reset_color()
                + color(255, 255, 255)
                + bg_color(32, 32, 32)
                + "]"
                + reset_color()
            )
            if code == JudgeResult.WA:
                out = (target_dir / "out" / f"sample-{i}.out").read_text().strip()
                line += (
                    "\n"
                    + bg_color(32, 64, 32)
                    + color(255, 255, 255)
                    + "\nExpected:\n"
                    + out
                    + reset_color()
                    + bg_color(64, 32, 32)
                    + color(255, 255, 255)
                    + "\nGot:\n"
                    + meta["stdout"].strip()
                    + reset_color()
                )
            elif code == JudgeResult.RE:
                err = meta["stderr"].strip()
                line += f" return code: {meta['return_code']}" + (
                    ("\n" + bg_color(64, 64, 32) + err + reset_color()) if err else ""
                )
            elif code == JudgeResult.TLE:
                line += (
                    bg_color(32, 32, 64)
                    + f" time: {meta['time']:.2f} sec"
                    + reset_color()
                )
            lines.append(line)
        lines.append(
            bg_color(32, 32, 32)
            + color(255, 255, 255)
            + "-" * (len(problem.name) + 34)
            + reset_color()
        )
        lines[-1].strip()

        for line in lines:
            print(line)
