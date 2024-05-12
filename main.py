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

print(atcoder.is_logged_in)
print(atcoder.alerts)


contest = atcoder.get_contest("https://atcoder.jp/contests/abc352")
print(contest)
# problem = atcoder.get_problem("https://atcoder.jp/contests/abc352/tasks/abc352_a")
# print(contest)
# print(contest.a)
atcoder.download_contest(contest)
