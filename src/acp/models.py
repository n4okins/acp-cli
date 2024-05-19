from pydantic import BaseModel


class AtCoderProblemsInfo(BaseModel):
    id: str
    title: str
    memo: str
    owner_user_id: int
    start_epoch_second: int
    duration_second: int
    mode: str | None
    is_public: bool
    penalty_second: int


class AtCoderProblemsInnerProblem(BaseModel):
    """
    AtCoder ProblemsのAPIの内部の問題データ
    """

    id: str
    point: None | int
    order: int


class AtCoderProblemsMetadata(BaseModel):
    """
    https://kenkoooo.com/atcoder/resources/problems.json から取得する問題のメタデータ
    """

    id: str
    contest_id: str
    problem_index: str
    name: str
    title: str
    url: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        self.url = f"https://atcoder.jp/contests/{self.contest_id}/tasks/{self.id}"


class AtCoderProblemsAPIResponse(BaseModel):
    info: AtCoderProblemsInfo
    problems: list[AtCoderProblemsInnerProblem]
