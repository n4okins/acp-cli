from src.acp.service import AtCoderProblems
from src.atcoder.service import AtCoder

acp = AtCoderProblems()
problems = acp.fetch_all_problems_metadata()
url = "https://kenkoooo.com/atcoder#/contest/show/e4b1a4f8-2043-4d70-8437-663152a8b700"
contest_data = acp.get_contest(url)
# acp.download_problems(contest_data)
acp.test("0")
acp.submit("0")
# atcoder.login(
#     username=env["ATCODER_USERNAME"],
#     password=env["ATCODER_PASSWORD"],
# )
# contest = atcoder.get_contest("https://atcoder.jp/contests/abc352")
# problem = atcoder.get_problem("https://atcoder.jp/contests/abc352/tasks/abc352_a")
# print(problem.root_dir)
# atcoder.download_problem(problem)
# atcoder.test(problem)
# print(problem, problem.name)
# print(contest)
# print(contest.a)
# atcoder.submit(problem)
# print(atcoder.get_latest_submission_results(problem))
