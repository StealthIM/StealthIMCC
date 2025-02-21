"""
学而思少儿编程 公共文件OSS
https://code.xueersi.com/

稳定性：⭐⭐⭐⭐
速度：⭐⭐⭐
安全性：⭐⭐⭐
限制少：⭐⭐⭐⭐⭐
推荐指数：⭐⭐⭐⭐
"""

import hashlib
import requests
import os
import json


def upload(relativeFilePath, token=None):
    absolutePath = os.path.abspath(relativeFilePath)
    return _uploadAbsolutePath(absolutePath)


def _uploadAbsolutePath(filepath):
    md5 = None
    contents = None
    if os.path.isfile(filepath):
        fp = open(filepath, 'rb')
        contents = fp.read()
        fp.close()
        md5 = hashlib.md5(contents).hexdigest()
    if md5 is None or contents is None:
        raise FileNotFoundError
    uploadParams = _getUploadParams(filepath, md5)
    requests.request(
        method="PUT", url=uploadParams['host'], data=contents, headers=uploadParams['headers'])
    return uploadParams['url']


def _getUploadParams(filename, md5):
    url = 'https://code.xueersi.com/api/assets/get_oss_upload_params'
    params = {"scene": "offline_python_assets",
              "md5": md5, "filename": filename}
    response = requests.get(url=url, params=params)
    data = json.loads(response.text)['data']

    return data
