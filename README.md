# acp-cli (AtCoder Problems Command Line Interface)

A command line interface for AtCoder Problems.

# Installation
```bash
$ pip install git+https://github.com/n4okins/acp-cli.git
```
```bash
$ rye install acp --git=https://github.com/n4okins/acp-cli.git
```

# Usage

### まず、AtCoderのユーザ名とパスワードを記載した.envファイルを作成してください。
```bash
$ echo "ATCODER_USERNAME=<your_atcoder_username>" >> .env
$ echo "ATCODER_PASSWORD=<your_atcoder_password>" >> .env
```
ディレクトリをgit管理している場合は`.gitignore`に`.env`を追加することを忘れないでください。
```bash
$ cat .env
ATCODER_USERNAME=<UserName>
ATCODER_PASSWORD=<Password>
```

# Commands
## Download virtual contest
```bash
$ acp d <AtCoder Virtual Contest URL>
```
ex:
```bash
$ acp d https://kenkoooo.com/atcoder/#/contest/show/07cc74a1-098e-4c51-9ac5-6121276d3c11
```
今回の例では「典型90問 難易度順」のコンテストをダウンロードします。以下のような出力が得られます。
ダウンロード先が問題無ければyを入力してください。

また、この際にカレントディレクトリ直下に`.acp`というディレクトリが作成されます。
ここにはキャッシュや最後にダウンロードしたコンテストのデータが保存されます。

`.env`同様、`.gitignore`に`.acp`を追加することを推奨します。

```
======================================== Virtual Contest: 典型90問 難易度順 ========================================
00 | typical90_d  - Cross Sum（★2）                         | https://atcoder.jp/contests/typical90/tasks/typical90_d
01 | typical90_j  - Score Sum Queries（★2）                 | https://atcoder.jp/contests/typical90/tasks/typical90_j
...
...
89 | typical90_cl - Tenkei90's Last Problem（★7）           | https://atcoder.jp/contests/typical90/tasks/typical90_cl
=============================================================================================================
Download problems in /path/to/典型90問 難易度順
Do you want to download problems in this directory? [y/N]:
```

## Test your code
```bash
$ acp t <problem_key>
```
`acp t`コマンドでテストケースの実行が可能です。
`<problem_key>`には問題のキーを指定してください。

デフォルトではPythonが実行されます。

整数を指定すると、直近にダウンロードしたコンテストの問題の中から指定した番号の問題をテストします。

キーに当てはまる問題が複数ヒットした場合は、一覧が表示されます。問題が特定できるようなキーを指定してください。

ex: 0番目の問題をテストする場合
```bash
$ acp t 0
Test <AtCoderProblem TYPICAL90- 'Cross Sum（★2）' - 0 [pts] (https://atcoder.jp/contests/typical90/tasks/typical90_d)> in '/path/to/典型90問 難易度順/00-typical90_d'? [y/N]: y
```
```
---------------- typical90_d ----------------
- Execute Directory:  '/path/to/典型90問 難易度順/00-typical90_d'
- Execute Command:    "python main.py"
---------------------------------------------
 sample-0   [ RE ] return code: 2
python: can't open file '/path/to/典型90問 難易度順/00-typical90_d/main.py': [Errno 2] No such file or directory
 sample-1   [ RE ] return code: 2
python: can't open file '/path/to/典型90問 難易度順/00-typical90_d/main.py': [Errno 2] No such file or directory
 sample-2   [ RE ] return code: 2
python: can't open file '/path/to/典型90問 難易度順/00-typical90_d/main.py': [Errno 2] No such file or directory
 sample-3   [ RE ] return code: 2
python: can't open file '/path/to/典型90問 難易度順/00-typical90_d/main.py': [Errno 2] No such file or directory
---------------------------------------------
```

まだ`main.py`が存在しないため、REが返されています。
各問題のディレクトリに`main.py`、あるいはコマンドで実行するファイルを作成することで、テストを行うことができます。
例えば、今回の例では`/path/to/典型90問 難易度順/00-typical90_d/main.py`を作成する必要があります。

ディレクトリ構成としては
```
/path/to/<Contest Title>/<Index>-<Problem ID>/in/sample-*.in
/path/to/<Contest Title>/<Index>-<Problem ID>/out/sample-*.out
/path/to/<Contest Title>/<Index>-<Problem ID>/main.py
```
のようになることを想定しています。

適切なファイルを作成した後、再度`acp t <problem_key>`を実行してください。

間違った出力が返された場合は、WAが返されます。
WAが返された場合は、期待される出力と実際の出力が表示されるので、それを参考に修正してください。
```
---------------- typical90_d ----------------
- Execute Directory:  '/path/to/典型90問 難易度順/00-typical90_d'
- Execute Command:    "python main.py"
---------------------------------------------
 sample-0   [ WA ]

Expected:
5 5 5
5 5 5
5 5 5
Got:
15 15 15
15 15 15
15 15 15
 sample-1   [ WA ]

Expected:
28 28 25 26
39 33 40 34
38 38 36 31
41 41 39 43
Got:
38 38 35 36
49 43 50 44
48 48 46 41
51 51 49 53
 sample-2   [ WA ]
...
...
---------------------------------------------
```
また、実行時間が超過するとTLEが返されます。
```
---------------- typical90_d ----------------
- Execute Directory:  '/path/to/典型90問 難易度順/00-typical90_d'
- Execute Command:    "python main.py"
---------------------------------------------
 sample-0   [ TLE ] time: 2.05 sec
 sample-1   [ TLE ] time: 2.03 sec
 sample-2   [ TLE ] time: 2.04 sec
 sample-3   [ TLE ] time: 2.04 sec
---------------------------------------------
```

デフォルトでは`python main.py`が実行されますが、実行するコマンドを変更したい場合は、`acp t <problem_key> -c <command>`を実行してください。


ex: C++などで作成した`./a.out`を実行する場合

この場合は`/path/to/典型90問 難易度順/00-typical90_d/a.out`が実行されます。
```bash
$ acp t 0 -c "./a.out"
Test <AtCoderProblem TYPICAL90- 'Cross Sum（★2）' - 0 [pts] (https://atcoder.jp/contests/typical90/tasks/typical90_d)> in '/path/to/典型90問 難易度順/00-typical90_d'? [y/N]:y
---------------- typical90_d ----------------
- Execute Directory:  '/path/to/典型90問 難易度順/00-typical90_d'
- Execute Command:    "./a.out"
---------------------------------------------
 sample-0   [ AC ]
 sample-1   [ AC ]
 sample-2   [ AC ]
 sample-3   [ AC ]
---------------------------------------------
```

## Submit your code
```bash
$ acp s <problem_key>
```
`acp s`コマンドで提出が可能です。
`<problem_key>`には問題のキーを指定してください。(testと同様です)
また、言語はデフォルトでは`5055 Python(CPython 3.11.4)`が実行されます。AtCoderで指定されている言語IDを指定することで、その言語で提出することができます。

```bash
$ acp s 0
language_id: 5055 (Python (CPython 3.11.4))
Submit '/path/to/典型90問 難易度順/00-typical90_d/main.py' to typical90_d? [y/N]: y
Submit /path/to/典型90問 難易度順/00-typical90_d/main.py to <AtCoderProblem TYPICAL90- 'Cross Sum（★2）' - 0 [pts] (https://atcoder.jp/contests/typical90/tasks/typical90_d)> ...
ジャッジ待ち 20XX-00-00 00:00:00+0900 | 004 - Cross Sum（★2） | <UserName> | Python (CPython 3.11.4) | 0 | 246 Byte | WJ
不正解 20XX-00-00 00:00:00+0900 | 004 - Cross Sum（★2） | <UserName> | Python (CPython 3.11.4) | 0 | 246 Byte | 2/16 WA
Submitted successfully. Please check the results. (https://atcoder.jp/contests/typical90/submissions/me)
```
提出後は5秒ごとにジャッジ結果を取得し、結果が返されると表示されます。
提出結果はAtCoderの提出結果ページでも確認できます。

使用できる言語は以下のコマンドで確認できます。
```bash
$ acp langs
ID: 5001 - C++ 20 (gcc 12.2)
ID: 5002 - Go (go 1.20.6)
...
ID: 5090 - COBOL (GnuCOBOL(Fixed) 3.1.2)
```

`grep`コマンドなどを組み合わせて、特定の言語のIDを取得することも可能です。
```bash
$ acp langs | grep "Python"
ID: 5055 - Python (CPython 3.11.4)
ID: 5063 - Python (Mambaforge / CPython 3.10.10)
ID: 5078 - Python (PyPy 3.10-v7.3.12)
ID: 5082 - Python (Cython 0.29.34)
```
`-l`オプションで言語IDを指定することができます。

`-f`オプションで提出するファイルを指定することができます。

```bash
$ acp s 0 -l 5028 -f ./main.cpp
language_id: 5028 (C++ 23 (gcc 12.2))
Submit '/path/to/典型90問 難易度順/00-typical90_d/main.cpp' to typical90_d? [y/N]: y
Submit /path/to/典型90問 難易度順/00-typical90_d/main.cpp to <AtCoderProblem TYPICAL90- 'Cross Sum（★2）' - 0 [pts] (https://atcoder.jp/contests/typical90/tasks/typical90_d)> ...
ジャッジ待ち 20XX-00-00 00:00:00+0900 | 004 - Cross Sum（★2） | <UserName> | C++ 23 (gcc 12.2) | 0 | 1058 Byte | WJ
ジャッジ中 20XX-00-00 00:00:00+0900 | 004 - Cross Sum（★2） | <UserName> | C++ 23 (gcc 12.2) | 0 | 1058 Byte | 1/16
正解 20XX-00-00 00:00:00+0900 | 004 - Cross Sum（★2） | <UserName> | C++ 23 (gcc 12.2) | 2 | 1058 Byte | AC | 337 ms | 44236 KB
Submitted successfully. Please check the results. (https://atcoder.jp/contests/typical90/submissions/me)
```
この例では、`/path/to/典型90問 難易度順/00-typical90_d/main.cpp`を、`C++ 23 (gcc 12.2)`で提出しています。



## Online-judge-tools互換？
### AtCoderの問題のURLを直接指定して、ダウンロード・テスト・提出を行うことができます。
#### Download
```bash
$ acp oj https://atcoder.jp/contests/typical90/tasks/typical90_a d
```
#### Test (python main.py)
```bash
$ acp oj https://atcoder.jp/contests/typical90/tasks/typical90_a t
>> Testing the problem from https://atcoder.jp/contests/typical90/tasks/typical90_a. executing python main.py on /path/to/typical90_a ...
---------------- typical90_a ----------------
- Execute Directory:  '/path/to/typical90/typical90_a'
- Execute Command:    "python main.py"
---------------------------------------------
 sample-0   [ AC ]
 sample-1   [ AC ]
 sample-2   [ AC ]
 sample-3   [ AC ]
 sample-4   [ AC ]
---------------------------------------------
```
#### Test (./a.out)
```bash
$ acp oj https://atcoder.jp/contests/typical90/tasks/typical90_a t -c "./a.out"
>> Testing the problem from https://atcoder.jp/contests/typical90/tasks/typical90_a. executing ./a.out on /path/to/typical90_a ...
---------------- typical90_a ----------------
- Execute Directory:  '/path/to/typical90/typical90_a'
- Execute Command:    "./a.out"
---------------------------------------------
 sample-0   [ AC ]
 sample-1   [ AC ]
 sample-2   [ AC ]
 sample-3   [ AC ]
 sample-4   [ AC ]
---------------------------------------------
```
#### Submit (main.py, Python)
```bash
$ acp oj https://atcoder.jp/contests/typical90/tasks/typical90_a s
>> Submit the solution to https://atcoder.jp/contests/typical90/tasks/typical90_a with main.py? [y/n] y
Submitting /path/to/typical90/typical90_a/main.py to typical90_a...
ジャッジ待ち 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | Python (CPython 3.11.4) | 0 | 503 Byte | WJ
ジャッジ中 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | Python (CPython 3.11.4) | 0 | 503 Byte | 14/29
正解 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | Python (CPython 3.11.4) | 4 | 503 Byte | AC | 191 ms | 20724 KB
Submitted successfully. Please check the results. (https://atcoder.jp/contests/typical90/submissions/me)
```
#### Submit (./main.cpp, C++)
```bash
$ acp oj https://atcoder.jp/contests/typical90/tasks/typical90_a s -l 5028 -f main.cpp
>> Submit the solution to https://atcoder.jp/contests/typical90/tasks/typical90_a with main.cpp? [y/n] y
Submitting /path/to/typical90/typical90_a/main.cpp to typical90_a...
ジャッジ待ち 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | C++ 23 (gcc 12.2) | 0 | 706 Byte | WJ
ジャッジ中 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | C++ 23 (gcc 12.2) | 0 | 706 Byte | 9/29
正解 20XX-00-00 00:00:00+0900 | 001 - Yokan Party（★4） | <UserName> | C++ 23 (gcc 12.2) | 4 | 706 Byte | AC | 32 ms | 4312 KB