from logging import basicConfig

from src.accprob.atcoder.service import AtCoder
from src.general.utils import load_env

basicConfig(level="INFO")

env = load_env()

atcoder = AtCoder()
atcoder.login(
    env.get("USERNAME", ""),
    env.get("PASSWORD", ""),
)
