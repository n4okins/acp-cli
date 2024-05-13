# acp-cli (AtCoder Problems Command Line Interface)

A command line interface for AtCoder Problems.

# Installation
```bash
pip install git+https://github.com/n4okins/acp.git
```

```bash
git clone https://github.com/n4okins/acp.git
cd acp
rye install
```
# Usage

### First, make .env file in the root directory of the project and add the following lines:
```bash
echo "ATCODER_USERNAME=<your_atcoder_username>" >> .env
echo "ATCODER_PASSWORD=<your_atcoder_password>" >> .env
```


# Commands
## Download Virtual Contest
```bash
acp d <contest_id>
```
ex:
```bash
acp d 
```