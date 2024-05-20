import enum
import subprocess
import time
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


__all__ = ["JudgeResult", "JudgeRunner"]


class JudgeResult(enum.Enum):
    """
    実行結果
    """

    AC = "AC"  # Accepted
    WA = "WA"  # Wrong Answer
    TLE = "TLE"  # Time Limit Exceeded
    RE = "RE"  # Runtime Error
    CE = "CE"  # Compile Error
    MLE = "MLE"  # Memory Limit Exceeded
    OLE = "OLE"  # Output Limit Exceeded
    IE = "IE"  # Internal Error


class JudgeRunner:
    """
    プログラムを実行し、結果を判定するクラス
    """

    def __init__(self, command: list[str], cd: Path | None = None) -> None:
        """
        Args:
            command (list[str]): 実行コマンド
            cd (Path | None, optional): 実行ディレクトリ. Defaults to None.
        
        Examples:
            >>> runner = JudgeRunner(["python3", "main.py"], Path("contest"))
        """
        self.command = command
        self.cd = cd or Path.cwd()
        logger.info("Command: %s", self.command)
        logger.info("Execute Directory: %s", self.cd)

    def run(
        self, input_testcase_file: Path | str, timeout: int = 60
    ) -> tuple[str, int, tuple[str, str]]:
        """
        Args:
            input_testcase_file (Path | str): 入力ファイル
            timeout (int, optional): タイムアウト秒数. Defaults to 60.

        Returns:
            tuple[str, int, tuple[str, str]]: 出力, リターンコード, (stdout, stderr)
        """
        input_testcase_file = (
            input_testcase_file
            if isinstance(input_testcase_file, Path)
            else Path(input_testcase_file)
        )
        proc = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cd,
        )
        stdout, stderr = proc.communicate(
            input=input_testcase_file.read_text().encode(), timeout=timeout
        )
        return (
            stdout.decode(),
            proc.returncode,
            (stdout.decode(), stderr.decode()),
        )

    def check(self, output_testcase_file: Path, answer: str) -> bool:
        """
        Args:
            output_testcase_file (Path): テストケース
            answer (str): 自分の答え
        
        Returns:
            bool: 正解かどうか (True: 正解, False: 不正解)
        """
        return output_testcase_file.read_text() == answer

    def __call__(
        self,
        input_testcase_file: Path,
        output_testcase_file: Path,
        timelimit: int = 2,
    ) -> tuple[JudgeResult, dict]:
        """
        Args:
            input_testcase_file (Path): 入力ファイル
            output_testcase_file (Path): テストケース
            timelimit (int, optional): タイムアウト秒数. Defaults to 2.
        
        Returns:
            tuple[JudgeResult, dict]: 判定結果, 実行結果
            
        """
        start = time.perf_counter()
        answer, return_code, (stdout, stderr) = self.run(input_testcase_file)
        t = time.perf_counter() - start
        logger.debug("Time: %f", t)

        code = JudgeResult.IE
        # 簡易的な判定
        if return_code != 0:
            code = JudgeResult.RE
        elif t > timelimit:
            code = JudgeResult.TLE
        elif not self.check(output_testcase_file, answer):
            code = JudgeResult.WA
        else:
            code = JudgeResult.AC
        return code, {
            "time": t,
            "return_code": return_code,
            "answer": answer,
            "stdout": stdout,
            "stderr": stderr,
        }
