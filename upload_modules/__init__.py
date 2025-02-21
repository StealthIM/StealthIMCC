from . import custom, xesoss, yiyunt
import db
import os

upload_lst = {
    "xesoss": xesoss.upload,
    "yiyunt": yiyunt.upload,
    "custom": custom.upload
}


def upload(file_path):
    if (not os.path.exists(file_path)):
        return (True, "找不到文件")
    module_name = db.get_info("set_img_api_module_name")
    key = db.get_info("set_img_api_key")
    if (module_name not in upload_lst):
        return (True, "模块不存在")
    if (key == ""):
        ret = upload_lst[module_name](file_path)
    else:
        ret = upload_lst[module_name](file_path, key)
    if (ret == ""):
        return (True, "上传失败")
    return (False, ret)
