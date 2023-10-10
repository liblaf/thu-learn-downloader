import subprocess
from subprocess import CompletedProcess


def username() -> str:
    process: CompletedProcess = subprocess.run(
        args=["bw", "--nointeraction", "get", "username", "id.tsinghua.edu.cn"],
        capture_output=True,
        text=True,
    )
    return process.stdout


def password() -> str:
    process: CompletedProcess = subprocess.run(
        args=["bw", "--nointeraction", "get", "password", "id.tsinghua.edu.cn"],
        capture_output=True,
        text=True,
    )
    return process.stdout
