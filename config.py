import json
import os
from yaml import safe_load


class Config:
    def __init__(self):
        self.now_dir = os.path.dirname(os.path.abspath(__file__))
        self.build_dir = os.path.join(self.now_dir, "build")
        if not os.path.exists(self.build_dir):
            os.mkdir(self.build_dir)
        self.latex_dir = os.path.join(self.build_dir, "latex")
        if not os.path.exists(self.latex_dir):
            os.mkdir(self.latex_dir)
        self.img_dir = os.path.join(self.build_dir, "img")
        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)
        self.latex_img_dir = os.path.join(self.latex_dir, "img")
        if not os.path.exists(self.latex_img_dir):
            os.mkdir(self.latex_img_dir)
        self.config_json_path = os.path.join(self.build_dir, "config.json")
        self.img_dict_path = os.path.join(self.build_dir, "img.json")
        yaml_path = os.path.join(self.now_dir, "config.yaml")
        with open(yaml_path, "rt", encoding="utf-8") as f:
            yaml_dict = safe_load(f)

        if not os.path.exists(self.config_json_path):
            self.config_json = {
                "title": yaml_dict["title"],
                "author": yaml_dict["author"]
            }
            self.save_config_json(self.config_json)
        else:
            self.config_json = self.load_config_json()
        self.md_src_dir = os.path.join(self.now_dir, yaml_dict["md_src_dir"])
        self.tex_dir = os.path.join(self.now_dir, "tex")
        self.temp_dir = os.path.join(self.build_dir, "temp")
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)

    def save_config_json(self, config_json: dict):
        with open(self.config_json_path, "wt", encoding="utf-8") as f:
            json.dump(config_json, f, indent=4, ensure_ascii=False)

    def load_config_json(self):
        with open(self.config_json_path, "rt", encoding="utf-8") as f:
            return json.load(f)


if __name__ == '__main__':
    param = Config()
    print(param)


