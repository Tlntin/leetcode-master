import os
import re
import PyPDF2
import pandas as pd
from tqdm import trange

now_dir = os.path.dirname(os.path.abspath(__file__))


def toc2level(toc_path: str, output_path: str):
    # first, parse toc file to level text
    with open(toc_path, "rt", encoding="utf-8") as f:
        text_list = f.readlines()
        result_data = []
        toc_data = ["目录", "Contents", 2]
        result_data.append(toc_data)
        for text in text_list:
            if r"\numberline" in text:
                text = text.split(r"\numberline")[-1].strip()
                # find page number
                p1 = re.compile("\{([0-9]+)\}")
                res1 = p1.search(text)
                page_num = 0
                if res1 is not None:
                    num_list = res1.groups()
                    if len(num_list) > 0:
                        page_num = int(num_list[0])
                if page_num == 0:
                    raise Exception("can't get page number from text, you may need rebuild newbook.tex. text is ", text)
                temp_text = text[: text.find("{" + str(page_num) + "}")]
                left = 0
                right = 0
                index = 0
                for word in temp_text:
                    index += 1
                    if word == "{":
                        left += 1
                    elif word == "}":
                        right += 1
                    if right == left > 0:
                        break
                level_text = temp_text[1: index - 1]
                note_text = temp_text[index: -1]

                level_text = level_text.replace("\\", "")
                p2 = re.compile("hspace.\{.*?\}")
                level_text = p2.sub("", level_text)
                # print(text, "\n", level_text, "\t", note_text, "\t", page_num)
                if note_text in ["周一", "周二"]:
                    continue
                # strip problem No
                note_text = note_text.strip().rstrip(".md").split(".")[-1].strip()
                if len(level_text) > 0 and len(note_text) > 0:
                    result_data.append([level_text, note_text, page_num])
            else:
                raise Exception("Error, can't found numberline in this, text is ", text)
        result_df = pd.DataFrame(result_data, columns=["level", "note", "page"])
        result_df.to_csv(output_path, index=False, encoding="utf-8")
        print("toc level path generate success, output path is ", output_path)


class PdfDirGenerator:

    def __init__(self, pdf_path: str, csv_path: str, offset: int = 0, out_path: str = None, levelmark: str = '.'):

        self.pdf_path = pdf_path  # pdf路径
        self.csv_path = csv_path  # 包含pdf目录信息的csv
        self.offset = offset  # 目录页数偏移量
        self.out_path = out_path  # 输出路径
        self.level_mark = levelmark  # 用于判断书签级别的标志符

        # 由于书签是有序的，我们只需保存/更新离子书签最近的父节点
        self.dir_parent = [None]

    def get_level_id(self, level):
        """计算书签的级数（级数的标志符号为“.”）
        一级目录: 0 个“.”，例如: 第1章、附录A等
            二级目录: 1个“.”，例如: 1.1、A.1
                三级目录: 2个“.”，例如: 2.1.3
        """
        mark_num = 0
        for c in level:
            if c == self.level_mark:
                mark_num += 1
        return mark_num + 1

    def run(self):

        print("--------------------------- Adding the bookmark ---------------------------")
        print(" * PDF Source: %s" % self.pdf_path)
        print(" * TXT Source: %s" % self.csv_path)
        print(" * Offset: %d" % self.offset)
        print("---------------------------------------------------------------------------")
        df1 = pd.read_csv(self.csv_path)
        pdf_reader = PyPDF2.PdfFileReader(self.pdf_path)
        pdf_writer = PyPDF2.PdfFileWriter()

        pdf_writer.cloneDocumentFromReader(pdf_reader)
        for i in trange(len(df1)):
            level = df1.loc[i, "level"]
            note = df1.loc[i, "note"]
            page = df1.loc[i, "page"]
            # 1. 计算当前的 level 的级数 id
            # 2. 插入书签的父结点存放在 dir_parent[id-1] 上
            # 3. 更新 dir_parent[id]
            level_id = self.get_level_id(level)
            if level_id >= len(self.dir_parent):
                self.dir_parent.append(None)
            self.dir_parent[level_id] = pdf_writer.addBookmark(
                level + ' ' + note, page - 1, self.dir_parent[level_id - 1]
            )

        if self.out_path is None:
            self.out_path = self.pdf_path[:-4] + '(书签).pdf'
        with open(self.out_path, 'wb') as out_pdf:
            pdf_writer.write(out_pdf)
            print("---------------------------------------------------------------------------")
            print(" * Save: %s" % self.out_path)
            print("---------------------------------- Done! ----------------------------------")


if __name__ == '__main__':
    toc_path1 = os.path.join(now_dir, "build", "newbook.toc")
    level_path1 = os.path.join(now_dir, "build", "toc_level.csv")
    toc2level(toc_path1, level_path1)
    pdf_path1 = os.path.join(now_dir, "build", "temp", "insert_page.pdf")
    pdf_generate = PdfDirGenerator(pdf_path=pdf_path1, csv_path=level_path1)
    pdf_generate.run()
