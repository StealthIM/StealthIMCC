"""
用户自定义图床源

稳定性：⭐⭐⭐⭐⭐
速度：⭐⭐⭐⭐⭐
安全性：⭐⭐⭐⭐⭐
推荐指数：⭐⭐⭐⭐⭐
"""


def upload(filename, token=""):  # 这里编写用户自己的逻辑
    ...

#        传统图床模板
#
# import requests
# def upload(image_path, token=""):
#     # 构建请求头
#     # 构建请求文件
#     files = {'%这里写你api的表单键名%': open(image_path, 'rb')}
#     # 发送POST请求
#     response = requests.post(
#         '%这里填写api的URL%', files=files)
#     # 关闭文件
#     files['%这里写你api的表单键名%'].close()
#     # 解析响应
#     if response.status_code == 200:
#         result = response.json()
#         if result["success"]:
#             return result["url"]
#         else:
#             return ""
#     else:
#         return ""
