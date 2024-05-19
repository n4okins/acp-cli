from pathlib import Path

from pydantic import BaseModel, ConfigDict
from pydantic.dataclasses import dataclass


class AtCoderProblem(BaseModel):
    difficulty: str
    url: str
    contest: "AtCoderContest"
    point: int
    title: str = ""
    name: str = ""
    is_interactive: bool = False
    root_dir: Path = Path.cwd()

    def __str__(self) -> str:
        return f"<AtCoderProblem {self.contest.name.upper()}-{self.difficulty} '{self.title}' - {self.point} [pts] ({self.url})>"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class AtCoderContest(BaseModel):
    name: str
    url: str
    problems: dict[str, AtCoderProblem] = {}
    points: dict[str, int] = {}

    def __getattr__(self, attr: str) -> AtCoderProblem:
        return self.problems[attr]

    def __getitem__(self, key: str) -> AtCoderProblem:
        return self.problems[key]

    def __str__(self) -> str:
        s = f"<AtCoderContest {self.name.upper()} {self.url}>"
        return s
