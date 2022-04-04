import os
import shutil
from tqdm import tqdm
import logging
import subprocess


class Logger(object):
    __path = None
    __level = logging.DEBUG
    __dict = {
        "info": logging.INFO,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "debug": logging.DEBUG
    }

    @classmethod
    def set_target(cls, path):
        """
        设置日志打印的目标位置,如果该路径不存在则创建.
        :param path:    str     日志打印的目标文件的路径
        :return:
        """
        # 从路径中提取目录路径
        directory = path[:-len(path.split("\\")[-1].split("/")[-1])-1]

        # 如果目录不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)

        cls.__path = path

    @classmethod
    def get_target(cls):
        """
        返回日志打印的目标位置.
        :return:
        """
        return cls.__path

    @classmethod
    def set_level(cls, level):
        """
        设置日志文件和Console窗口中记录的日志级别.
        :param level:   str     可选"info"、"error"、"warning"和"debug"不区分大小写
        :return:
        """
        # 检查输入的日志级别是否合法
        if level.lower() not in ["info", "error", "warning", "debug"]:
            raise ValueError("Only info|error|warning|debug is available.")

        cls.__level = cls.__dict[level.lower()]

    @classmethod
    def get_level(cls):
        """
        获取打印的日志级别.
        :return:
        """
        return cls.__level

    def log(self, msg, level="info"):
        """
        将日志输出到屏幕.
        :param msg:     str     要打印的日志信息
        :param level:   str     可选"info"、"error"、"warning"和"debug"不区分大小写
        :return:
        """
        # 检查输入的日志级别是否合法
        if level.lower() not in ["info", "error", "warning", "debug"]:
            raise ValueError("Only info|error|warning|debug is available.")

        # 设置日志打印格式
        format_ = "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s"

        # 开启输出到日志文件的打印器
        logging.basicConfig(
            filename=self.get_target(),
            filemode="a",
            format=format_,
            level=self.get_level()
        )

        # 开启输出到Console的打印器
        console = logging.StreamHandler()
        console.setLevel(self.get_level())
        formatter = logging.Formatter(format_)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        # 将日志打印到日志文件和Console页面
        logging.log(self.__dict[level.lower()], msg)

        # 关闭Console打印器否则会重复打印
        logging.getLogger('').removeHandler(console)

now_dir = os.path.dirname(os.path.abspath(__file__))
latex_dir = os.path.join(now_dir, "build", "latex")
img_dir = os.path.join(now_dir, "build", "img")
new_latex_dir = os.path.join(now_dir, "build", "temp_latex")
new_img_dir = os.path.join(new_latex_dir, "img")
if not os.path.exists(new_latex_dir):
    os.mkdir(new_latex_dir)
if not os.path.exists(new_img_dir):
    os.mkdir(new_img_dir)
for file in os.listdir(img_dir):
    shutil.copy(
        os.path.join(img_dir, file),
        os.path.join(new_img_dir, file)
    )
head_latex_path = os.path.join(now_dir, "head.tex")
with open(head_latex_path, "rt", encoding="utf-8") as f:
    head_text = f.read()
tqdm_iter = tqdm(os.listdir(latex_dir))
for file in tqdm_iter:
    tqdm_iter.set_description("convert markdown latex to full latex")
    src_file_path = os.path.join(latex_dir, file)
    des_file_path = os.path.join(new_latex_dir, file)
    if not src_file_path.endswith(".tex"):
        continue
    latex_text = head_text + "\n"
    latex_text += r"\begin{document}"
    latex_text += "\n"
    with open(src_file_path, "rt", encoding="utf-8") as f:
        # print(src_file_path)
        text = f.read()
        # print(text)
        latex_text += text
        latex_text += r"\end{document}"
        latex_text += "\n"
    with open(des_file_path, "wt", encoding="utf-8") as f:
        f.write(latex_text)

# try to compile new latex
log = Logger()
log_dir = os.path.join(now_dir, "log")
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
log_path = os.path.join(log_dir, "md_compile_log.txt")
if os.path.exists(log_path):
    os.remove(log_path)
log.set_target(log_path)
file_list = os.listdir(latex_dir)
file_list = [file for file in file_list if file.endswith(".tex")]
file_list.sort(key=lambda x: int(x.split(".")[0]))
for idx, file in enumerate(file_list):
    file_path = os.path.join(new_latex_dir, file)
    log.log("file path: {}".format(file_path))
    res = subprocess.Popen(
        "cd {} && xelatex -synctex=1 -interaction=nonstopmode -file-line-error --shell-escape {}".format(new_latex_dir, file_path),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
    )
    try:
        stdout, stderr = res.communicate(timeout=10)
        log.log(stdout.decode())
        if len(stderr) > 0:
            log.log("Error: " + stdout.decode())
    except Exception as err:
        log.log("Error: timeout of subprocess")





