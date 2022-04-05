"""
picture download
latex can't show internet image, we need download it!
"""
import requests
import os
import time
import json
from random import random
import hashlib
from config import Config


params = Config()


if not os.path.exists(params.img_dict_path):
    img_dict = {}  # save url to img path
else:
    with open(params.img_dict_path, "rt", encoding="utf-8") as f:
        img_dict = json.load(f)


def img_down(img_url: str, img_path=None):
    headers = {
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/85.0.4183.102 Safari/537.36"
    }
    old_img_path = img_dict.get(img_url, None)
    if old_img_path is not None:
        old_img_path2 = os.path.join(params.build_dir, old_img_path)
        if os.path.exists(old_img_path2):
            return old_img_path
    res = requests.get(img_url, headers=headers)
    if res.status_code == 200:
        content = res.content
        if img_path is None:
            md5obj = hashlib.md5()
            md5obj.update(content)
            img_hash = md5obj.hexdigest()
            if ".gif" in img_url:
                img_type = ".gif"
            elif ".jpg" in img_url:
                img_type = ".jpg"
            elif ".jpeg" in img_url:
                img_type = ".jpeg"
            elif ".tif" in img_url:
                img_type = ".tif"
            elif ".tiff" in img_url:
                img_type = ".tiff"
            else:
                img_type = ".png"
            img_path1 = os.path.join(params.img_dir, img_hash + img_type)
            img_path2 = os.path.join(params.latex_img_dir, img_hash + img_type)
            img_path = os.path.join("img", img_hash + img_type)
            img_dict[img_url] = img_path
            with open(img_path1, "wb") as f1:
                f1.write(content)
            with open(img_path2, "wb") as f2:
                f2.write(content)
            with open(params.img_dict_path, "wt", encoding="utf-8") as f2:
                json.dump(img_dict, f2, indent=4)
        time.sleep(random() / 2)
        return img_path
    else:
        print(img_url, "can't download")
        return None


if __name__ == "__main__":
    img_url1 = "https://img-blog.csdnimg.cn/20201119173039835.png"
    img_down(img_url1)




