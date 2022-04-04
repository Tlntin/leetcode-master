import json
import os
import re
from tqdm import tqdm
from img_down import img_down

now_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(now_dir, "build")
img_dir = os.path.join("build", "img")

# table of content path
toc_path = os.path.join(now_dir, "toc.md")
src_dir = "problems"

if not os.path.exists(toc_path):
    print("you must add toc.md in here!")

# latex dir
latex_dir = os.path.join(build_dir, "latex")


def get_md_path(sent: str):
    """
    :param sent:
    :return:
    """
    file_path = None
    p = re.compile("\[.*\]\((.*?)\)")
    res = p.search(sent)
    if res is not None:
        path_list = res.groups()
        path_list = [
            t_path for t_path in path_list if
            t_path.lower().endswith("md")
        ]
        if len(path_list) > 0:
            file_path = path_list[0]
    return file_path


def strip_md_text(md_sent_list: list, toc_degree: int, md_file_path=None):
    """
    1. lower header degree, because we need article head degree is lower than it's toc
    2. Remove redundant consecutive spaces
    :param md_sent_list:
    :param toc_degree: table of contents degree
    :param md_file_path
    :return:
    """
    # first, we can Remove redundant consecutive spaces
    left = 0
    del_idx_list = []
    md_sent_list = [sent.strip("\n") for sent in md_sent_list]
    for idx, sent in enumerate(md_sent_list):
        if len(sent) == 0:
            if len(md_sent_list[left]) > 0:
                left = idx
        else:
            if len(md_sent_list[left]) == 0:
                if (idx - left) > 2:
                    del_idx_list.extend(list(range(left, idx - 1)))
                left = idx
    else:
        # delete tail blank
        if len(md_sent_list[left]) == 0 and len(md_sent_list) - left > 2:
            del_idx_list.extend(list(range(left, len(md_sent_list))))

    for idx in del_idx_list[::-1]:
        md_sent_list.pop(idx)
    # second, get highest degree in now text
    # when we need to parse head by "#", we need ignore note
    note_count = 0
    head_data_list = []
    for idx, sent in enumerate(md_sent_list):
        word_list = sent.split()
        if len(word_list) > 0:
            if sent.startswith("```"):
                note_count += 1
            elif word_list[0].startswith("#") and note_count % 2 == 0:
                head_degree = word_list[0].count("#")
                head_data_list.append([idx, head_degree])
    if len(head_data_list) > 0:
        # highest_degree = min([data[1] for data in head_data_list])
        # if highest_degree < toc_degree + 1:
        #     need_add = toc_degree + 1 - highest_degree
        #     need_add_str = '#' * need_add
        # else:
        #     need_add_str = ""
        need_add_str = "#" * (toc_degree + 1)
        # make other header to be item
        for index, head_data in enumerate(head_data_list):
            idx = head_data[0]
            if index == 0:
                md_sent_list[idx] = need_add_str + md_sent_list[idx].lstrip("#")
            else:
                md_sent_list[idx] = "- **" + md_sent_list[idx].lstrip("#").lstrip() + "**"
    else:
        print(md_file_path, " can't found head in here, please check")
    return "\n".join(md_sent_list)


def get_md_text(file_path: str, toc_degree: int):
    """
    read markdown and pare content
    :param file_path:
    :param toc_degree
    :return:
    """
    with open(file_path, "rt", encoding="utf-8") as f2:
        md_text_list = f2.readlines()  # need add syntax check
        md_text_list = [
            t_text for t_text in md_text_list
            if not t_text.lstrip().startswith("<")
        ]
        # download internet img and replace img url to local picture
        md_text_list2 = []
        for t_text in md_text_list:
            p = re.compile("!\[.*?\]\((.*?)\)")
            res22 = p.search(t_text)
            if res22 is not None:
                url_list = res22.groups()
                if len(url_list) > 0:
                    img_url = url_list[0]
                    img_path = img_down(img_url)
                    if img_path is not None:
                        if not img_path.endswith(".gif"):
                            t_text = t_text.replace(img_url, img_path)
                        else:
                            # there are som problem in gif with latex
                            # So we need change gif to url
                            t_text = t_text.replace("![", "[")
                    else:
                        print(img_path, "download failed")
                        t_text = ""
            md_text_list2.append(t_text)
        md_text = strip_md_text(md_text_list2, toc_degree, file_path)
        return md_text


def save_markdown_latex(latex_content: str, output_path: str, clear_page: bool = False):
    """
    save markdown content to file path
    :param latex_content:
    :param output_path:
    :param clear_page: use \clearpage function to make new page
    :return:
    """
    with open(output_path, "wt", encoding="utf-8") as f:
        f.write(r"\begin{markdown}")
        f.write("\n")
        f.write(latex_content)
        f.write("\n")
        f.write(r"\end{markdown}")
        f.write("\n")
        if clear_page:
            f.write(r"\clearpage")
            f.write("\n")


def generate_book_latex(latex_path_list: list, toc_len = 2):
    # generate latex
    head_latex_file = os.path.join(now_dir, "head.tex")
    latex_text = ""
    with open(head_latex_file, "rt", encoding="utf-8") as f:
        latex_text += f.read()
        latex_text += "\n"
    latex_text += r"\begin{document}"
    latex_text += "\n"
    latex_text += r"\maketitle"
    latex_text += "\n"
    latex_text += r"\tableofcontents"
    latex_text += "\n"
    # when you get real page length, you can add black page to perpare
    if toc_len > 2:
        for i in range(toc_len - 2):
            latex_text += r"\newpage"
            latex_text += "\n"
            latex_text += r"\mbox{}"
            latex_text += "\n"
        latex_text += r"\newpage"
        latex_text += "\n"
    for latex_file in latex_path_list:
        latex_text += r"    \input{" + latex_file.split(".")[0] + "}\n"
    latex_text += r"\end{document}"
    result_latex_file = os.path.join(build_dir, "book.tex")
    with open(result_latex_file, "wt", encoding="utf-8") as f:
        f.write(latex_text)
    print("book.tex generated success, save in ", result_latex_file)
    print("now you can build pdf or epub with book.tex")


def main():
    latex_file_list = []
    latex2md_path = {}
    # read toc file
    print("start reading markdown file")
    toc_degree = 0
    toc_page = 7  # the page of table of content
    with open(toc_path, "rt", encoding="utf-8") as f:
        file_index = 1
        for text in tqdm(f.readlines()):
            # judgement caption
            if len(text.split()) == 0:
                continue
            text_type = text.split()[0]
            md_file_path = get_md_path(text)
            if md_file_path is not None:
                md_file_path = os.path.join(src_dir, md_file_path.lstrip("./"))
            latex_file_path = os.path.join(latex_dir, f"{file_index}.tex")

            if md_file_path is not None:
                if not os.path.exists(md_file_path):
                    print(md_file_path, "not exists")
                    continue
                md_text = get_md_text(md_file_path, toc_degree)
                save_markdown_latex(md_text, latex_file_path, True)
                latex2md_path[latex_file_path] = md_file_path
                latex_file_list.append(latex_file_path)
            elif text_type.startswith("#"):
                toc_degree = text_type.count('#')
                save_markdown_latex(text, latex_file_path, False)
                latex_file_list.append(latex_file_path)
            file_index += 1
    generate_book_latex(latex_file_list, toc_page)
    trans_path = os.path.join(build_dir, "latex2md.json")
    with open(trans_path, "wt", encoding="utf-8") as f:
        json.dump(latex2md_path, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    # md_sent_list1 = [
    #     "# caption 1", "```python", "# this note", "print(Hello World)",
    #     "```", "", "", "", "", "# caption 2", "", "", "",  "## subject 3",
    #     "", "", ""
    # ]
    # test_file = "/Users/hfy/leetcode-master/problems/1207.独一无二的出现次数.md"
    # # test_file = os.path.join(latex_dir, "4.tex")
    # with open(test_file, "rt", encoding="utf-8") as f:
    #     md_sent_list1 = f.readlines()
    # toc_degree1 = 2
    # result_text = strip_md_text(md_sent_list1, toc_degree1)
    # print(result_text)
    main()