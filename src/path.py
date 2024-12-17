import os
import sys

def get_resource_path(relative_path = None):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller 创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

base = get_resource_path(".")
prefabs = get_resource_path("prefabs")
server = get_resource_path("server")
configs = get_resource_path("configs")
src = get_resource_path("src")