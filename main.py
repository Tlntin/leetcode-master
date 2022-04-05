import os
import subprocess
from utils.generate_latex import generate_latex
from utils.md_check import pre_compile_latex, convert_full_latex
from utils.find_error import find_error, find_failed_md


def check_latex_env():
    print("=" * 20)
    print("start check you latex environment..")
    res1 = subprocess.Popen(
        "latex --version", shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, close_fds=True
    )
    stdout, stderr = res1.communicate(timeout=10)
    if len(stderr) > 0:
        raise Exception("you may not install latex")
    else:
        print(stdout.decode())
    res2 = subprocess.Popen(
        "xelatex --version", shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, close_fds=True
    )
    stdout2, stderr2 = res2.communicate(timeout=10)
    if len(stderr2) > 0:
        raise Exception("you should install live-latex again!")
    else:
        print(stdout2.decode())
    print("It's seems you latex install ok!")
    print("=" * 20)


if __name__ == '__main__':
    # 1. check you environment
    check_latex_env()
    # 2. generate latex for book
    generate_latex()
    # 3. pre compile latex, it may take a lot of time,
    # convert_full_latex()
    # pre_compile_latex()
    # # 4. find error latex
    # find_error()
    # find_failed_md()
