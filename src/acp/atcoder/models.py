from pathlib import Path

from pydantic import BaseModel, ConfigDict


class AtCoderProblem(BaseModel):
    """
    AtCoderの問題1つを表すモデル
    """

    difficulty: str
    url: str
    contest: "AtCoderContest"
    point: int
    title: str = ""
    name: str = ""
    is_interactive: bool = False
    root_dir: Path = Path.cwd()

    def __str__(self) -> str:
        return f"<AtCoderProblem {self.contest.name.upper()} {('-' + self.difficulty + ' ') if self.difficulty else ''}'{self.title}' - {self.point} [pts] ({self.url})>"


class AtCoderContest(BaseModel):
    """
    AtCoderのコンテストを表すモデル
    """

    name: str
    url: str
    problems: dict[str, AtCoderProblem] = dict()
    points: dict[str, int] = dict()

    model_config = ConfigDict(arbitrary_types_allowed=True)  # pydanticの設定

    def __getattr__(self, attr: str) -> AtCoderProblem:
        # self.a などで問題を取得できるようにする
        return self.problems[attr]

    def __getitem__(self, key: str) -> AtCoderProblem:
        # self["a"] などで問題を取得できるようにする
        return self.problems[key]

    def __str__(self) -> str:
        s = f"<AtCoderContest {self.name.upper()} {self.url}>"
        return s
