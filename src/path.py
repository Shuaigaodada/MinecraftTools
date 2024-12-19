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

def set_base(path):
    global base
    base = path

def set_prefabs(path):
    global prefabs
    prefabs = path

def set_server(path):
    global server
    server = path

def set_configs(path):
    global configs
    configs = path

def set_src(path):
    global src
    src = path

base = get_resource_path(".")
prefabs = get_resource_path("prefabs")
server = get_resource_path("server")
configs = get_resource_path("configs")
src = get_resource_path("src")