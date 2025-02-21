"""
一云公共图床
https://imgbed.yiyunt.cn/

稳定性：⭐⭐
速度：⭐⭐⭐⭐⭐
安全性：⭐⭐⭐
限制少：⭐⭐⭐
推荐指数：⭐⭐⭐
"""
import requests


def upload(image_path, token=""):
    # 构建请求头
    # 构建请求文件
    files = {'fileupload': open(image_path, 'rb')}

    # 发送POST请求
    response = requests.post(
        'https://imgbed.yiyunt.cn/api/upload/'+token, files=files)

    # 关闭文件
    files['fileupload'].close()

    # 解析响应
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["url"]
        else:
            return ""
    else:
        return ""
