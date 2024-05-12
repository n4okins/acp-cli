from logging import basicConfig

from src.atcoder.service import AtCoder
from src.general.utils import load_env

basicConfig(level="INFO")

env = load_env()

atcoder = AtCoder()
atcoder.login(
    username=env["ATCODER_USERNAME"],
    password=env["ATCODER_PASSWORD"],
)
# contest = atcoder.get_contest("https://atcoder.jp/contests/abc352")
problem = atcoder.get_problem("https://atcoder.jp/contests/abc352/tasks/abc352_a")
atcoder.download_problem(problem)
print(problem, problem.name)
# print(contest)
# print(contest.a)
atcoder.test(problem)