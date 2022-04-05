import os
import shutil
from tqdm import tqdm
import subprocess
from config import Config


params = Config()


def convert_full_latex():
    new_latex_dir = os.path.join(params.build_dir, "temp_latex")
    new_img_dir = os.path.join(new_latex_dir, "img")

    if not os.path.exists(new_latex_dir):
        os.mkdir(new_latex_dir)
    if not os.path.exists(new_img_dir):
        os.mkdir(new_img_dir)
    for file in os.listdir(params.img_dir):
        shutil.copy(
            os.path.join(params.img_dir, file),
            os.path.join(new_img_dir, file)
        )
    head_latex_path = os.path.join(params.tex_dir, "head.tex")
    with open(head_latex_path, "rt", encoding="utf-8") as f:
        head_text = f.read()
    tqdm_iter = tqdm(os.listdir(params.latex_dir))
    for file in tqdm_iter:
        tqdm_iter.set_description("convert markdown latex to full latex")
        src_file_path = os.path.join(params.latex_dir, file)
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


def pre_compile_latex():
    # try to compile new latex
    log_dir = os.path.join(params.build_dir, "log")
    new_latex_dir = os.path.join(params.build_dir, "temp_latex")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_path = os.path.join(log_dir, "md_compile_log.txt")
    if os.path.exists(log_path):
        os.remove(log_path)
    file_list = os.listdir(params.latex_dir)
    file_list = [file for file in file_list if file.endswith(".tex")]
    file_list.sort(key=lambda x: int(x.split(".")[0]))
    with open(log_path, "wt", encoding="utf-8") as f:
        tqdm_iter = tqdm(file_list)
        for file in tqdm_iter:
            tqdm_iter.set_description("pre compile latex")
            file_path = os.path.join(new_latex_dir, file)
            f.write("file path: {}\n".format(file_path))
            res = subprocess.Popen(
                "cd {} && xelatex -synctex=1 -interaction=nonstopmode -file-line-error --shell-escape {}"\
                    .format(new_latex_dir, file_path),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
            )
            try:
                stdout, stderr = res.communicate(timeout=10)
                f.write(stdout.decode() + "\n")
                if len(stderr) > 0:
                    f.write("Error: " + stdout.decode() + "\n")
            except Exception as err:
                f.write("Error: timeout of subprocess\n")


if __name__ == '__main__':
    convert_full_latex()
    pre_compile_latex()





