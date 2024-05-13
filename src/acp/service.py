import json
from logging import getLogger
from pathlib import Path

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

        self.problems_metadata = {}

    def login_atcoder(self, root_dir: Path) -> AtCoder:
        atcoder_client = AtCoder()
        try:
            env = load_env(root_dir / ".env")
        except FileNotFoundError:
            raise self.AtCoderProblemsExceptions.LoginFailedError(
                f"Please make .env file at {root_dir / '.env'}"
            )
        username = env.get("USERNAME", env.get("ATCODER_USERNAME", None))
        password = env.get("PASSWORD", env.get("ATCODER_PASSWORD", None))

        if not username or not password:
            raise self.AtCoderProblemsExceptions.LoginFailedError(
                "Please set (ATCODER_USERNAME | USERNAME) and (ATCODER_PASSWORD | PASSWORD) in .env"
            )

        atcoder_client.login(username=username, password=password)
        return atcoder_client

    def write_cache(
        self, cache_dir: Path, data: dict, filename: Path | str = "cache.json"
    ) -> None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        if (cache_dir / filename).exists():
            prev = self.read_cache(cache_dir)
            prev.update(data)
            data = prev
        with (cache_dir / filename).open("w") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4,
            )

    def read_cache(self, cache_dir: Path, filename: Path | str = "cache.json") -> dict:
        if (cache_dir / filename).exists():
            with (cache_dir / filename).open("r") as f:
                return json.load(f)
        return {}

    def guess_cache_dir(self, root_dir: Path = Path.cwd()) -> Path:
        cache_path = root_dir / ".acp"
        if not cache_path.exists():
            for parent in root_dir.parents:
                cache_path = parent / ".acp"
                root_dir = parent
                if cache_path.exists():
                    break
        return Path.cwd() / ".acp"

    def fetch_all_problems_metadata(self) -> dict[str, AtCoderProblemsMetadata]:
        url = "https://kenkoooo.com/atcoder/resources/problems.json"
        cache_dir = self.guess_cache_dir()
        cache = self.read_cache(cache_dir, "metadata.json")
        if cache:
            return {x["id"]: AtCoderProblemsMetadata(**x) for x in cache}
        else:
            self.get(url)
            metadata = {
                x["id"]: AtCoderProblemsMetadata(**x) for x in self.response.json()
            }
            self.write_cache(cache_dir, self.response.json(), "metadata.json")
            return metadata

    def get_contest(self, url: str) -> AtCoderProblemsAPIResponse:
        if "#/contest/show/" not in url:
            raise self.AtCoderProblemsExceptions.ContestNotFoundError(
                f"Failed to find contest in {url}"
            )
        url = url.replace(
            "#/contest/show", "internal-api/contest/get"
        )  # APIのURLに変換
        self.get(url)
        data = self.response.json()
        data["problems"] = [AtCoderProblemsInnerProblem(**x) for x in data["problems"]]
        data = AtCoderProblemsAPIResponse(**data)

        print("=" * 40 + f" Virtual Contest: {data.info.title} " + "=" * 40)
        max_name_length = max(len(problem.id) for problem in data.problems)
        self.problems_metadata = self.fetch_all_problems_metadata()
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
            target_dir = (
                self.guess_cache_dir().parent / "contests" / contest_data.info.title
            )
        target_dir = Path(target_dir)
        print(f"Download problems in {target_dir}")
        if confirm_yn_input(
            "Do you want to download problems in this directory? [y/N]: "
        ):
            atcoder = self.login_atcoder(self.guess_cache_dir().parent)
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

            root_dir = self.guess_cache_dir()
            self.write_cache(
                root_dir,
                {
                    "contest": contest_data.model_dump(),
                    "target_dir": str(target_dir.relative_to(root_dir.parent)),
                },
            )
            with open(target_dir / "info.json", "w") as f:
                json.dump(problems, f, indent=2)

    def guess_problem(self, key: str, info_file: Path) -> AtCoderProblem:
        with info_file.open("r") as f:
            data = json.load(f)
            if key.isdigit():
                problem_data = list(data.values())[int(key)]
            else:
                problem_data = data.get(key, None)
                if problem_data is None:
                    candidate = tuple(
                        filter(
                            lambda x: (key in x["contest"]["url"])
                            or (key in x["contest"]["name"])
                            or (key in x["name"])
                            or (key in x["root_dir"])
                            or (key in x["title"])
                            or (key in x["url"]),
                            data.values(),
                        )
                    )
                    if len(candidate) == 1:
                        problem_data = candidate[0]
                    elif len(candidate) > 1:
                        msg = f"\nAmbiguous problem name: {key}\n\n"
                        for i, problem in enumerate(candidate):
                            msg += f"{i:02d} | {problem['name']} - {problem['contest']['url']}\n"

                        msg += "\nPlease specify the problem name."
                        raise self.AtCoderProblemsExceptions.AmbiguousProblemError(msg)
                    else:
                        raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                            f"Failed to find {key} in {info_file}"
                        )

            return AtCoderProblem(**problem_data)

    def test(
        self,
        name: str,
        command: list[str] = ["python", "main.py"],
        target_dir: Path | str | None = None,
    ) -> None:
        cache_path = self.guess_cache_dir()
        root_dir = cache_path.parent
        cache = self.read_cache(cache_path)
        target_dir = target_dir or root_dir / cache["target_dir"]
        target_dir = Path(target_dir)
        if not target_dir.exists():
            raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                f"Failed to find problems in {target_dir}"
            )

        info_file = target_dir / "info.json"
        if not info_file.exists():
            raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                f"Failed to find problems in {target_dir}"
            )
        target_problem = self.guess_problem(name, info_file)
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

    def submit(
        self,
        name: str,
        *,
        submit_file: Path | str = "main.py",
        language_id: int = 5055,  # Python (CPython 3.11.4)
        target_dir: Path | str | None = None,
    ) -> None:
        root_dir = Path.cwd()
        cache_path = root_dir / ".acp"
        if not cache_path.exists():
            for parent in root_dir.parents:
                cache_path = parent / ".acp"
                root_dir = parent
                if cache_path.exists():
                    break

        cache = self.read_cache(cache_path)
        target_dir = target_dir or root_dir / cache["target_dir"]
        target_dir = Path(target_dir)
        if not target_dir.exists():
            raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                f"Failed to find problems in {target_dir}"
            )

        info_file = target_dir / "info.json"
        if not info_file.exists():
            raise self.AtCoderProblemsExceptions.ProblemsNotFoundError(
                f"Failed to find problems in {target_dir}"
            )
        target_problem = self.guess_problem(name, info_file)
        submit_file = target_dir / target_problem.root_dir / submit_file
        print(
            f"language_id: {language_id} ({AtCoder._cache['lang'].get(language_id, 'Unknown')})"
        )
        if confirm_yn_input(
            f"Submit '{submit_file}' to {target_problem.name}? [y/N]: "
        ):
            atcoder = self.login_atcoder(root_dir)
            print(f"Submit {submit_file} to {target_problem} ...")
            atcoder.submit(
                target_problem, submit_file=submit_file, language_id=language_id
            )
        else:
            print("Abort submitting.")
            return
