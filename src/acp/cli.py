import argparse
from pathlib import Path

from .atcoder.service import AtCoder
from .service import AtCoderProblems

__version__ = "0.1.0"


def main():
    parser = argparse.ArgumentParser("AtCoder Problems command line tools")
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    acp = AtCoderProblems()
    subparsers = parser.add_subparsers(required=True)
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

    def download_hook(args) -> None:
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
            "ex: python main.py"
            "**/<Problem_DIR>/sample-*.in **/<Problem_DIR>/sample-*.out"
        ),
        default="python main.py",
    )
    t.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help="The directory of the contest",
        default=None,
    )

    def test_hook(args) -> None:
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
        default="main.py",
    )
    s.add_argument(
        "--language",
        "-l",
        metavar="<Language ID>",
        help="The language ID of the file",
        default="5055",
    )
    s.add_argument(
        "--directory",
        "-d",
        metavar="<Directory Path>",
        help="The directory of the contest",
        default=None,
    )

    def submit_hook(args) -> None:
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

    def status_hook(args) -> None:
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

    def languages_hook(args) -> None:
        for id_, lang in AtCoder._cache["lang"].items():
            print(f"ID: {id_} - {lang}")

    languages.set_defaults(func=languages_hook)

    args = parser.parse_args()
    args.func(args)

    # t = subparsers.add_parser(
    #     "test",
    #     description="Test the solution",
    #     help="Require the file to test",
    #     aliases=["t"],
    # )
    # t.add_argument(
    #     "problem",
    #     metavar="<Problem Index> OR <Problem ID>",
    #     help="The problem index or ID to test. (ex: if the directory is '01-abc001_a', \
    #         the problem index is '01' and the problem ID is 'abc001_a')",
    # )
    # t.add_argument(
    #     "--skip-confirm",
    #     dest="skip_confirm",
    #     action="store_true",
    #     help="Skip the confirmation",
    # )
    # t.add_argument(
    #     "-y",
    #     "--yes",
    #     dest="skip_confirm",
    #     action="store_true",
    #     help="Skip the confirmation",
    # )
    # t.add_argument(
    #     "--show-detail",
    #     dest="show_detail",
    #     action="store_true",
    #     help="Show the detail of the test result",
    # )
    # t.add_argument(
    #     "--bind-commands",
    #     metavar="<Command>",
    #     help=(
    #         "Bind the command to test the solution. Tester will run"
    #         "`<Command> **/sample-*.in **/sample-*.out`)"
    #         "ex: python main.py"
    #         "**/<Problem_DIR>/sample-*.in **/<Problem_DIR>/sample-*.out"
    #     ),
    #     default="python main.py",
    # )

    # def test_hook(args) -> None:
    #     AtCoderProblems(args.url, args.directory).test(
    #         args.problem,
    #         args.bind_commands,
    #         not_confirm=args.skip_confirm,
    #         show_detail=args.show_detail,
    #     )

    # t.set_defaults(func=test_hook)

    # d.set_defaults(func=download_hook)

    # s = subparsers.add_parser(
    #     "submit",
    #     description="Submit the solution to the contest",
    #     help="Require the file to submit",
    #     aliases=["s"],
    # )
    # s.add_argument("file", metavar="<File Path>", help="The file to submit")

    # def submit_hook(args) -> None:
    #     AtCoderProblems(args.url).submit(args.file)

    # s.set_defaults(func=submit_hook)
