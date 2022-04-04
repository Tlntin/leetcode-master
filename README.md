### 文件说明
1. `toc.md`: 目录文件，由原版的README.md修改得来
2. `generate_latex.py`, 该文件主要用于读取目录文件，以及生成latex, 功能特性如下：
- 将jpg, png文件缓存到本地, gif变成超链接
- 去除html标签，因为转latex会有Bug,导致编译失败
- 去除连续多个空格
- 保留首个#标题，如果目录是2级，该标题自动变成3级标题。
3. `md_check.py`, 检查每个markdown文件格式，并且将每个markdown转成latex, 预编译一次，看看是否会报错，并且保留编译日志。
4. `find_error.py`, 从预编译的日志中查找错误，并且将对应的markdown文件所对应的latex注释掉，防止编译不过。
5. `generate_note`, 从.toc文件中获取书签，然后导入到pdf中。
6. `img_down.py` 下载markdown中的图片，不包括html标签图片
7. `head.tex` markdown转latex的通用latex文件。
8. `toc.tex` 手动编译目录的latex文件

### 构建指南
0. 配置好textlive, VScode环境。
1. 运行`generate_latex.py`, 生成build/book.tex
2. 运行`md_check.py`, 预编译每个markdown, 生成预编译日志.
3. 运行`find_error.py`, 从预编译日志中找到报错的markdown latex, 自动注释掉，生成build/newbook.tex.
4. 编译`build/newbook.tex`, 生成newbook.pdf文件。
5. 如果第四步出现错误，手动注释掉`build/newbook.tex`的22.tex那一行。
6. 查看`newbook.pdf`, 看看是否有目录（理论上应该没有，因为有报错），如果没有，则需要手动生成目录。
7. 手动生成目录方法，在build目录下新建一个temp文件夹，将`build/newbook.toc`与项目根目录的`toc.tex`丢进去，编译toc.tex，生成toc.pdf，其中包含7页目录。
8. 将手动目录添加到newbook.pdf的方法，可以用pdf编辑软件安装，也可以把`insert_page.tex`, `build/newbook.pdf`丢到第7步的文件夹，然后编译`insert_page.tex`即可。(注意newbook.pdf的页码总数是否为1482，如果不是记得修改一下咯)
9. 运行generate_note导入书签到目标pdf。

### 其他说明
1. 如何保证手动添加的目录与newbook.pdf页码对齐？
  - 默认的目录是2页，如果手动生成的toc.pdf是7页，只需要提前插入5页空白页占位就可以了。
  - 可以通过修改generate_latex.py中的main函数，修改215行来控制生成的空白目录页数量。（当前为7页）