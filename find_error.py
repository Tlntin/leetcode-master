import os
import re
import json

now_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(now_dir, "build")
latex_dir = os.path.join(build_dir, "latex")
error_file = os.path.join("build", "log", "md_compile_log.txt")
error_json = os.path.join("build", "log", "error.json")
# if not os.path.exists(error_json):
#     error_dict = {}
# else:
#     with open(error_json, "rt", encoding="utf-8") as f:
#         error_dict = json.load(f)


def find_error():
    error_dict = {}
    with open(error_file, "rt", encoding="utf-8") as f:
        text_file = ""
        error_str = ""
        p1 = re.compile("build/temp_latex/([0-9]+)\.tex")
        p2 = re.compile("Error(.*)")
        result_data_dict = {}
        text_list = f.readlines()
        for idx, text in enumerate(text_list):
            # print(text)
            # if "latex" in text:
            #     print(text)
            res1 = p1.search(text)
            if res1 is not None:
                temp_list1 = res1.groups()
                if len(temp_list1) > 0:
                    text_file = os.path.join(latex_dir, temp_list1[0])
                    # print(text_file)
            res2 = p2.search(text)
            if res2 is not None:
                temp_list2 = res2.groups()
                if len(temp_list2) > 0:
                    error_str = temp_list2[0] + " ".join(text_list[idx + 1: idx + 2])
                    if len(text_file) > 0:
                        result_data_dict[text_file] = error_str
        # print error, and ignore error file
        with open(os.path.join(build_dir, "book.tex"), "rt", encoding="utf-8") as f2:
            book_latex = f2.read()
        start_idx = 0
        for k, v in result_data_dict.items():
            error_dict[k] = v
            print(k, " --> ", v)

            # temp insert
            k = k.replace("/Users/hfy/PycharmProjects/gea", "/Users/hfy/leetcode-master")
            # ignore error file
            # error_input_file = r"\input{" + k + "}"
            # print(error_input_file)
            file_index = book_latex[start_idx:].find(k)
            if file_index > 0:
                file_index += (start_idx - 10)
                book_latex = book_latex[: file_index] + "% " + book_latex[file_index:]
                start_idx = file_index
            print(k, " --> ", file_index, " --> ", book_latex[file_index: file_index + len(k) + 12])
        # print(book_latex)

        with open(error_json, "wt", encoding="utf-8") as f2:
            json.dump(error_dict, f2, indent=4)
        print("error json save in ",  error_json)

        with open(os.path.join(build_dir, "newbook.tex"), "wt", encoding="utf-8") as f2:
            f2.write(book_latex)


def find_failed_md():
    with open(os.path.join(build_dir, "newbook.tex"), "rt", encoding="utf-8") as f2:
        text_list = f2.readlines()
    trans_path = os.path.join(build_dir, "latex2md.json")
    with open(trans_path, "rt", encoding="utf-8") as f3:
        latex2md_dict = json.load(f3)
    start = None
    print("start print failed markdown where it can't be compiled to latex")
    for idx, text in enumerate(text_list):
        text = text.strip()
        if text == r"\begin{document}":
            start = idx
        if start is not None:
            if text.startswith("%"):
                p = re.compile("\{(.*?)\}")
                res = p.search(text)
                if res is not None:
                    temp_list = res.groups()
                    if len(temp_list) > 0:
                        latex_path = temp_list[0] + ".tex"
                        md_path = latex2md_dict[latex_path]
                        print(md_path)


if __name__ == '__main__':
    find_failed_md()

