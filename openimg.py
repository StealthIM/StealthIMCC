import requests
import sys
import config
import os
import hashlib
import getchar
import subprocess
import db

IMG_PATH = config.IM_CFG_PATH+os.sep+"session"+os.sep+"user"+os.sep+"img"


def open_img(url):
    if not os.path.exists(IMG_PATH):
        os.makedirs(IMG_PATH)
    file_name = hashlib.md5(url.encode("utf-8")).hexdigest()
    file_path = IMG_PATH+os.sep+file_name
    sys.stdout.write(f"\033[2J\033[1;1H")
    sys.stdout.write(f"\033[34m从 \033[90m\"{url}\"\033[0m 下载图片中\033[0m...")
    sys.stdout.flush()
    if not os.path.exists(file_path):
        try:
            req = requests.get(url).content
            with open(file_path, "wb") as f:
                f.write(req)
        except requests.exceptions.ConnectionError:
            sys.stdout.write(f"\033[2J\033[1;1H")
            sys.stdout.write(
                f"\033[31m下载图片失败，请检查网络连接\033[0m\r\n\033[90m[任意键继续]\033[0m")
            sys.stdout.flush()
            getchar.get_char()
            return False
        except PermissionError:
            sys.stdout.write(f"\033[2J\033[1;1H")
            sys.stdout.write(
                f"\033[31m下载图片失败，请检查权限\033[0m\r\n\033[90m[任意键继续]\033[0m")
            sys.stdout.flush()
            return False
    sys.stdout.write(f"\033[2J\033[1;1H\033[0m")
    sys.stdout.flush()
    if db.get_info("set_img_open_wait") == "true":
        # getchar.disable_base_mode()
        os.system(db.get_info(
            "set_img_open_cmd").replace("%s", file_path))
        sys.stdout.write(
            f"\r\n\r\n\033[90m[任意键继续]\033[0m")
        sys.stdout.flush()
        # input()
        getchar.get_char()
        # getchar.enable_base_mode()
    else:
        subprocess.Popen(db.get_info(
            "set_img_open_cmd").replace("%s", file_path), shell=True)
