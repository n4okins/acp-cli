import json
from logging import getLogger
from pathlib import Path

from bs4 import BeautifulSoup

from src.acp.models import (
    AtCoderProblemsAPIResponse,
    AtCoderProblemsInnerProblem,
    AtCoderProblemsMetadata,
)
from src.atcoder.models import AtCoderProblem
from src.atcoder.service import AtCoder
from src.general.service import WebService
from src.general.utils import confirm_yn_input, load_env

logger = getLogger(__name__)


class AtCoderProblems(WebService):
    class URLs:
        BASE = "https://kenkoooo.com/atcoder"
        # ex: https://kenkoooo.com/atcoder#/contest/show/e4b1a4f8-2043-4d70-8437-663152a8b700

    class AtCoderProblemsExceptions(WebService.Exceptions):
        class ContestNotFoundError(Exception):
            pass

        class AmbiguousProblemError(Exception):
            pass

    def __init__(self, parser: str = "lxml") -> None:
        super().__init__(parser)

        self.problems_metadata = self.fetch_all_problems_metadata()

    def login_atcoder(self) -> AtCoder:
        atcoder_client = AtCoder()
        try:
            env = load_env()
        except FileNotFoundError:
            raise self.AtCoderProblemsExceptions.LoginFailedError(
                f"Please make .env file at {Path.cwd() / '.env'}"
            )
        username = env.get("USERNAME", env.get("ATCODER_USERNAME", None))
        password = env.get("PASSWORD", env.get("ATCODER_PASSWORD", None))

        if not username or not password:
            raise self.AtCoderProblemsExceptions.LoginFailedError(
                "Please set (ATCODER_USERNAME | USERNAME) and (ATCODER_PASSWORD | PASSWORD) in .env"
            )

        atcoder_client.login(username=username, password=password)
        return atcoder_client

    def write_cache(self, cache_dir: Path, data: dict) -> None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        if (cache_dir / "cache.json").exists():
            prev = self.read_cache(cache_dir)
            prev.update(data)
            data = prev
        with (cache_dir / "cache.json").open("w") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
            )

    def read_cache(self, cache_dir: Path) -> dict:
        if (cache_dir / "cache.json").exists():
            with (cache_dir / "cache.json").open("r") as f:
                return json.load(f)
        return {}

    def fetch_all_problems_metadata(self) -> dict[str, AtCoderProblemsMetadata]:
        cache = self.read_cache(Path.cwd() / ".acp")
        if "metadata" in cache:
            return {x["id"]: AtCoderProblemsMetadata(**x) for x in cache["metadata"]}
        url = "https://kenkoooo.com/atcoder/resources/problems.json"
        self.get(url)
        metadata = {x["id"]: AtCoderProblemsMetadata(**x) for x in self.response.json()}
        self.write_cache(
            Path.cwd() / ".acp",
            {"metadata": [x.model_dump() for x in metadata.values()]},
        )
        return metadata

    def get_contest(self, url: str) -> AtCoderProblemsAPIResponse:
        if "#/contest/show/" not in url:
            raise self.AtCoderProblemsExceptions.ContestNotFoundError(
                f"Failed to find contest in {url}"
            )
        url = url.replace(
            "#/contest/show", "/internal-api/contest/get"
        )  # APIのURLに変換
        self.get(url)
        data = self.response.json()
        data["problems"] = [AtCoderProblemsInnerProblem(**x) for x in data["problems"]]
        data = AtCoderProblemsAPIResponse(**data)

        print("=" * 40 + f" Virtual Contest: {data.info.title} " + "=" * 40)
        max_name_length = max(len(problem.id) for problem in data.problems)
        max_title_length = max(
            len(self.problems_metadata[problem.id].title) for problem in data.problems
        )
        for i, problem in enumerate(data.problems):
            metadata = self.problems_metadata[problem.id]
            print(
                f"{i:02d} | {problem.id + (' ' * (max_name_length - len(problem.id)))} - {metadata.name + (' ' * (max_title_length - len(metadata.title)))} | {metadata.url}"
            )
        print("=" * (40 * 2 + len(f" Virtual Contest: {data.info.title} ")))

        return data

    def download_problems(
        self,
        contest_data: AtCoderProblemsAPIResponse,
        target_dir: Path | str | None = None,
    ) -> None:
        if target_dir is None:
            target_dir = Path.cwd() / "contests" / contest_data.info.title
        target_dir = Path(target_dir)
        print(f"Download problems in {target_dir}")
        if confirm_yn_input(
            "Do you want to download problems in this directory? [y/N]: "
        ):
            atcoder = self.login_atcoder()
            target_dir.mkdir(parents=True, exist_ok=True)
            problems = {}
            for i, problem in enumerate(contest_data.problems):
                metadata = self.problems_metadata[problem.id]
                problem_dir = target_dir / f"{i:02d}-{metadata.id}"
                problem_dir.mkdir(parents=True, exist_ok=True)
                problem_data = atcoder.get_problem(metadata.url)
                problems[problem_data.name] = problem_data.model_dump()
                problems[problem_data.name]["root_dir"] = str(
                    problem_dir.relative_to(target_dir)
                )
                atcoder.download_problem(problem_data, problem_dir)
                print(f"Downloaded {metadata.id} to {problem_dir}")
                self.wait(0.25)

            self.write_cache(
                Path.cwd() / ".acp",
                {
                    "contest": contest_data.model_dump(),
                    "target_dir": str(target_dir.relative_to(Path.cwd())),
                },
            )
            with open(target_dir / "info.json", "w") as f:
                json.dump(problems, f, indent=2)

    def test(
        self,
        name: str,
        command: list[str] = ["python", "main.py"],
        target_dir: Path | str | None = None,
    ) -> None:
        cache = self.read_cache(Path.cwd() / ".acp")
        if not cache:
            for parent in Path.cwd().parents:
                cache = self.read_cache(parent / ".acp")
                if cache:
                    break

        target_dir = target_dir or Path.cwd() / cache["target_dir"]
        target_dir = Path(target_dir)
        if not target_dir.exists():
            raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                f"Failed to find problems in {target_dir}"
            )
        with (target_dir / "info.json").open("r") as f:
            data = json.load(f)
            if name.isdigit():
                problem_data = list(data.values())[int(name)]
            else:
                problem_data = data.get(name, None)
                if problem_data is None:
                    candidate = tuple(
                        filter(
                            lambda x: (name in x["contest"]["url"])
                            or (name in x["contest"]["name"])
                            or (name in x["name"])
                            or (name in x["root_dir"])
                            or (name in x["title"])
                            or (name in x["url"]),
                            data.values(),
                        )
                    )
                    if len(candidate) == 1:
                        problem_data = candidate[0]
                    elif len(candidate) > 1:
                        msg = f"\nAmbiguous problem name: {name}\n\n"
                        for i, problem in enumerate(candidate):
                            msg += f"{i:02d} | {problem['name']} - {problem['contest']['url']}\n"

                        msg += "\nPlease specify the problem name."
                        raise self.AtCoderProblemsExceptions.AmbiguousProblemError(msg)
                    else:
                        raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                            f"Failed to find {name} in {target_dir}"
                        )

            target_problem = AtCoderProblem(**problem_data)
            if confirm_yn_input(
                f"Test {target_problem} in '{target_dir / target_problem.root_dir}'? [y/N]:"
            ):
                AtCoder().test(
                    target_problem,
                    target_dir=target_dir / target_problem.root_dir,
                    command=command,
                )
            else:
                print("Abort testing.")
                return
