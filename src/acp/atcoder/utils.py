import sys


def force_input(prompt: str) -> str:
    """
    強制的に入力を取得する
    入力が空文字の場合は再度入力を促す
    Args:
        prompt (str): プロンプト

    Returns:
        str: 入力された文字列

    """
    x = input(prompt)
    while True:
        try:
            if x:
                return x
            x = input(prompt)
        except KeyboardInterrupt:
            print("Interrupted. Exiting...")
            sys.exit(1)
        except EOFError:
            print("EOF. Exiting...")
            sys.exit(1)
