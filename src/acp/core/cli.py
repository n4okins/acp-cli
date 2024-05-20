import argparse
from pathlib import Path

from acp.atcoder.service import AtCoder
from acp.core.__version__ import __version__
from acp.core.service import AtCoderProblems

# TODO: コンフィグファイルで設定できるようにする
DEFAULT_EXEC_COMMAND = "python main.py"
DEFAULT_SUBMIT_FILE = "main.py"
DEFAULT_SUBMIT_LANG = 5055


def main() -> None:
    parser = argparse.ArgumentParser("AtCoder Problems command line tools")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    acp = AtCoderProblems()
    subparsers = parser.add_subparsers(required=True)
    oj = subparsers.add_parser(
        "online-judge-tools",
        description="As a equivalent of online-judge-tools",
        help="Require the URL of the contest",
        aliases=["oj"],
    )
    oj.add_argument(
        "url",
        metavar="<AtCoder URL>",
        help="URL of problem page of AtCoder",
    )
    oj.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help="The directory of the contest",
        default=Path.cwd(),
        type=Path,
    )
    oj_parsers = oj.add_subparsers(required=False)
    oj_d = oj_parsers.add_parser(
        "download",
        description="Download the test cases of the contest",
        help="Require the URL of the contest (default)",
        aliases=["d"],
    )
    oj_t = oj_parsers.add_parser(
        "test",
        description="Test the solution",
        help="Require the file to test",
        aliases=["t"],
    )
    oj_t.add_argument(
        "--command",
        "-c",
        metavar="<Command>",
        help=(
            "Bind the command to test the solution. Tester will run"
            "`<Command> **/sample-*.in **/sample-*.out`)"
            f"ex: {DEFAULT_EXEC_COMMAND}"
            "**/<Problem_DIR>/sample-*.in **/<Problem_DIR>/sample-*.out"
        ),
        default=DEFAULT_EXEC_COMMAND,
    )
    oj_s = oj_parsers.add_parser(
        "submit",
        description="Submit the solution to the contest",
        help="Require the file to submit",
        aliases=["s"],
    )
    oj_s.add_argument(
        "--file",
        "-f",
        metavar="<File Path>",
        help="The file to submit",
        default=DEFAULT_SUBMIT_FILE,
        type=Path,
    )
    oj_s.add_argument(
        "--language",
        "-l",
        metavar="<Language ID>",
        help="The language ID of the file",
        default=DEFAULT_SUBMIT_LANG,
        type=int,
    )

    def oj_download_hook(args: argparse.Namespace) -> None:
        print(
            f"Downloading the problem from {args.url} into {args.directory / args.url.split('/')[-1]} ..."
        )
        atc = AtCoderProblems().login_atcoder(args.directory)
        p = atc.get_problem(args.url)
        atc.download_problem(p)

    def oj_test_hook(args: argparse.Namespace) -> None:
        root = args.directory / args.url.split("/")[-1]
        print(
            f"Testing the problem from {args.url}. executing {args.command} on {root} ..."
        )
        atc = AtCoderProblems().login_atcoder(args.directory)
        p = atc.get_problem(args.url)
        atc.test(p, command=args.command.split())

    def oj_submit_hook(args: argparse.Namespace) -> None:
        atc = AtCoderProblems().login_atcoder(args.directory)
        p = atc.get_problem(args.url)
        atc.submit(p, submit_file=args.file, language_id=args.language)

    oj_d.set_defaults(func=oj_download_hook)
    oj_t.set_defaults(func=oj_test_hook)
    oj_s.set_defaults(func=oj_submit_hook)

    oj.set_defaults(func=oj_download_hook)

    d = subparsers.add_parser(
        "download",
        description="Download the test cases of the contest",
        help="Require the URL of the contest",
        aliases=["d"],
    )
    d.add_argument(
        "url",
        metavar="<AtCoder Problems URL>",
        help="URL of the virtual contest of AtCoder Problems",
    )
    d.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help=f"The directory to create contest directory. \
            default: currnet directory ({Path.cwd() / '<Virtual Contest Name>'})",
        default=Path.cwd(),
    )

    def download_hook(args: argparse.Namespace) -> None:
        contest = acp.get_contest(args.url)
        acp.download_problems(
            contest, Path(args.directory).resolve() / contest.info.title
        )

    d.set_defaults(func=download_hook)

    t = subparsers.add_parser(
        "test",
        description="Test the solution",
        help="Require the file to test",
        aliases=["t"],
    )
    t.add_argument(
        "problem",
        metavar="<Problem Index> OR <Problem ID>",
        help=" (Allow ambiguous input)\n  The problem index or ID to test. (ex: if the directory is '01-abc001_a', \
            the problem index is '01' and the problem ID is 'abc001_a')",
    )
    t.add_argument(
        "--command",
        "-c",
        metavar="<Command>",
        help=(
            "Bind the command to test the solution. Tester will run"
            "`<Command> **/sample-*.in **/sample-*.out`)"
            f"ex: {DEFAULT_EXEC_COMMAND}"
            "**/<Problem_DIR>/sample-*.in **/<Problem_DIR>/sample-*.out"
        ),
        default=DEFAULT_EXEC_COMMAND,
    )
    t.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help="The directory of the contest",
        default=None,
    )

    def test_hook(args: argparse.Namespace) -> None:
        acp.test(args.problem, args.command.split(), args.directory)

    t.set_defaults(func=test_hook)

    s = subparsers.add_parser(
        "submit",
        description="Submit the solution to the contest",
        help="Require the file to submit",
        aliases=["s"],
    )
    s.add_argument(
        "problem", metavar="<Problem Index>", help="The problem index to submit"
    )
    s.add_argument(
        "--file",
        "-f",
        metavar="<File Path>",
        help="The file to submit",
        default=DEFAULT_SUBMIT_FILE,
    )
    s.add_argument(
        "--language",
        "-l",
        metavar="<Language ID>",
        help="The language ID of the file",
        default=DEFAULT_SUBMIT_LANG,
    )
    s.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help="The directory of the contest",
        default=None,
    )

    def submit_hook(args: argparse.Namespace) -> None:
        acp.submit(
            args.problem,
            submit_file=args.file,
            language_id=int(args.language),
            target_dir=args.directory,
        )

    s.set_defaults(func=submit_hook)

    status = subparsers.add_parser(
        "status",
        description="Show the status of latest joined contests",
    )

    def status_hook(_: argparse.Namespace) -> None:
        cache = acp.read_cache(acp.guess_cache_dir())
        msg = ""
        if cache:
            msg += "Joined contests: "
            msg += f"{cache['contest']['info']['title']}"
            msg += f" at {Path.cwd() / cache['target_dir']}"

        else:
            msg += "No joined contests"
        print(msg)

    status.set_defaults(func=status_hook)

    languages = subparsers.add_parser(
        "langs",
        description="Show the supported languages",
    )

    def languages_hook(_: argparse.Namespace) -> None:
        for id_, lang in AtCoder._cache["lang"].items():
            print(f"ID: {id_} - {lang}")

    languages.set_defaults(func=languages_hook)

    args = parser.parse_args()
    args.func(args)
