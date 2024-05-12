import json
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
    _cache: dict = {
        "submit": {},
        "lang": {
            5001: "C++ 20 (gcc 12.2)",
            5002: "Go (go 1.20.6)",
            5003: "C# 11.0 (.NET 7.0.7)",
            5004: "Kotlin (Kotlin/JVM 1.8.20)",
            5005: "Java (OpenJDK 17)",
            5006: "Nim (Nim 1.6.14)",
            5007: "V (V 0.4)",
            5008: "Zig (Zig 0.10.1)",
            5009: "JavaScript (Node.js 18.16.1)",
            5010: "JavaScript (Deno 1.35.1)",
            5011: "R (GNU R 4.2.1)",
            5012: "D (DMD 2.104.0)",
            5013: "D (LDC 1.32.2)",
            5014: "Swift (swift 5.8.1)",
            5015: "Dart (Dart 3.0.5)",
            5016: "PHP (php 8.2.8)",
            5017: "C (gcc 12.2.0)",
            5018: "Ruby (ruby 3.2.2)",
            5019: "Crystal (Crystal 1.9.1)",
            5020: "Brainfuck (bf 20041219)",
            5021: "F# 7.0 (.NET 7.0.7)",
            5022: "Julia (Julia 1.9.2)",
            5023: "Bash (bash 5.2.2)",
            5024: "Text (cat 8.32)",
            5025: "Haskell (GHC 9.4.5)",
            5026: "Fortran (gfortran 12.2)",
            5027: "Lua (LuaJIT 2.1.0-beta3)",
            5028: "C++ 23 (gcc 12.2)",
            5029: "Common Lisp (SBCL 2.3.6)",
            5030: "COBOL (Free) (GnuCOBOL 3.1.2)",
            5031: "C++ 23 (Clang 16.0.6)",
            5032: "Zsh (Zsh 5.9)",
            5033: "SageMath (SageMath 9.5)",
            5034: "Sed (GNU sed 4.8)",
            5035: "bc (bc 1.07.1)",
            5036: "dc (dc 1.07.1)",
            5037: "Perl (perl  5.34)",
            5038: "AWK (GNU Awk 5.0.1)",
            5039: "なでしこ (cnako3 3.4.20)",
            5040: "Assembly x64 (NASM 2.15.05)",
            5041: "Pascal (fpc 3.2.2)",
            5042: "C# 11.0 AOT (.NET 7.0.7)",
            5043: "Lua (Lua 5.4.6)",
            5044: "Prolog (SWI-Prolog 9.0.4)",
            5045: "PowerShell (PowerShell 7.3.1)",
            5046: "Scheme (Gauche 0.9.12)",
            5047: "Scala 3.3.0 (Scala Native 0.4.14)",
            5048: "Visual Basic 16.9 (.NET 7.0.7)",
            5049: "Forth (gforth 0.7.3)",
            5050: "Clojure (babashka 1.3.181)",
            5051: "Erlang (Erlang 26.0.2)",
            5052: "TypeScript 5.1 (Deno 1.35.1)",
            5053: "C++ 17 (gcc 12.2)",
            5054: "Rust (rustc 1.70.0)",
            5055: "Python (CPython 3.11.4)",
            5056: "Scala (Dotty 3.3.0)",
            5057: "Koka (koka 2.4.0)",
            5058: "TypeScript 5.1 (Node.js 18.16.1)",
            5059: "OCaml (ocamlopt 5.0.0)",
            5060: "Raku (Rakudo 2023.06)",
            5061: "Vim (vim 9.0.0242)",
            5062: "Emacs Lisp (Native Compile) (GNU Emacs 28.2)",
            5063: "Python (Mambaforge / CPython 3.10.10)",
            5064: "Clojure (clojure 1.11.1)",
            5065: "プロデル (mono版プロデル 1.9.1182)",
            5066: "ECLiPSe (ECLiPSe 7.1_13)",
            5067: "Nibbles (literate form) (nibbles 1.01)",
            5068: "Ada (GNAT 12.2)",
            5069: "jq (jq 1.6)",
            5070: "Cyber (Cyber v0.2-Latest)",
            5071: "Carp (Carp 0.5.5)",
            5072: "C++ 17 (Clang 16.0.6)",
            5073: "C++ 20 (Clang 16.0.6)",
            5074: "LLVM IR (Clang 16.0.6)",
            5075: "Emacs Lisp (Byte Compile) (GNU Emacs 28.2)",
            5076: "Factor (Factor 0.98)",
            5077: "D (GDC 12.2)",
            5078: "Python (PyPy 3.10-v7.3.12)",
            5079: "Whitespace (whitespacers 1.0.0)",
            5080: "><> (fishr 0.1.0)",
            5081: "ReasonML (reason 3.9.0)",
            5082: "Python (Cython 0.29.34)",
            5083: "Octave (GNU Octave 8.2.0)",
            5084: "Haxe (JVM) (Haxe 4.3.1)",
            5085: "Elixir (Elixir 1.15.2)",
            5086: "Mercury (Mercury 22.01.6)",
            5087: "Seed7 (Seed7 3.2.1)",
            5088: "Emacs Lisp (No Compile) (GNU Emacs 28.2)",
            5089: "Unison (Unison M5b)",
            5090: "COBOL (GnuCOBOL(Fixed) 3.1.2)",
        }
    }

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
            contest=contest
            or AtCoderContest(
                name=url.split("/")[-3], url="/".join(url.split("/")[:-2])
            ),
            point=point,
        )
        self.get(problem.url)
        if not self._cache["lang"]:
            try:
                for lang in self.soup.find_all("option"):
                    if lang.text:
                        self._cache["lang"][int(lang["value"])] = lang.text
            except KeyError:
                pass

        self.wait(0.25)
        title = self.soup.find("span", class_="h2")
        if title is None:
            msg = f"Title not found in {problem.url}. Is the problem ID correct?"
            raise self.AtCoderExceptions.ProblemsNotFoundError(msg)
        problem.title = title.text.strip().split("\n")[0].split(" - ")[1]
        problem.name = problem.url.split("/")[-1]
        problem.root_dir = Path.cwd() / problem.contest.name / problem.name.lower()
        return problem

    def download_problem(
        self, problem: AtCoderProblem, target_dir: str | Path | None = None
    ) -> None:
        target_dir = Path(target_dir) if target_dir else problem.root_dir

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
            else target_dir or problem.root_dir
        )

        runner = JudgeRunner(command=command, cd=target_dir)
        lines = []
        lines.append(
            color(255, 255, 255)
            + "-" * 16
            + " "
            + problem.name
            + " "
            + "-" * 16
            + f"\n- Execute Directory:  '{target_dir}'\n"
            + '- Execute Command:    "'
            + " ".join(command)
            + '"\n'
            + "-" * (len(problem.name) + 34)
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
                + f" sample-{i}   "
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

    def guess_directory(self, problem: AtCoderProblem) -> Path:
        cd = Path.cwd()
        standard = cd / problem.contest.name / problem.name.lower()
        if standard.exists():
            return standard
        for p in cd.iterdir():
            if p.is_dir() and problem.name in p.name:
                return p
        return cd

    def submit(
        self,
        problem: AtCoderProblem,
        *,
        submit_file: Path | str = "main.py",
        language_id: int = 5055,  # Python (CPython 3.11.4)
    ):
        submit_file = Path(submit_file) if isinstance(submit_file, str) else submit_file
        if not submit_file.is_absolute():
            submit_file = problem.root_dir / submit_file
        if not submit_file.exists():
            submit_file = self.guess_directory(problem) / submit_file.name
        if not submit_file.exists():
            raise FileNotFoundError(f"{submit_file} not found.")
        submit_url = problem.contest.url + "/submit"
        self.get(submit_url)
        self.wait(0.1)
        form: bs4.Tag = self.soup.find(
            "form", action=f"/contests/{problem.contest.name.lower()}/submit"
        )  # type: ignore
        csrf_token = form.find("input", attrs={"name": "csrf_token"})["value"]  # type: ignore
        data = {
            "data.TaskScreenName": problem.name,
            "data.LanguageId": language_id,
            "sourceCode": submit_file.read_text(),
            "csrf_token": csrf_token,  # type: ignore,
        }
        self.post(submit_url, data=data)
        self.wait(1)
        for i in range(10):
            self.get(problem.contest.url + "/submissions/me", use_cache=False)
            latest = BeautifulSoup(self.response.text, self.parser)
            judge = latest.find("span", class_="label").attrs["title"]
            status = [td.text.strip() for td in latest.find_all("tr")[1].find_all("td")][:-1]
            print(judge, " | ".join(status))
            if judge not in ["ジャッジ待ち", "ジャッジ中"]:
                break
            self.wait(3)
        else:
            print("Time out.")


        # self.wait(1)
        # for i in range(30):
        #     latest = BeautifulSoup(
        #         self.get_latest_submission_results(problem)["Html"],
        #         self.parser,
        #     )
        #     judge = latest.find("span", class_="label").attrs["title"]
        #     status = [td.text for td in latest.find_all("td")]
        #     print(judge, status)
        #     if judge not in ["ジャッジ待ち", "ジャッジ中"]:
        #         break
        #     self.wait(1)

    # def get_latest_submission_results(self, problem: AtCoderProblem):
    #     submit_results_url = problem.contest.url + "/submissions/me/status/json"
    #     self.get(submit_results_url, use_cache=False)
    #     data = json.loads(self.soup.text)
    #     print(data)
    #     return tuple(data["Result"].items())[-1][1]
