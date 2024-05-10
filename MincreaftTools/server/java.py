import requests
from typing import Optional
from server import Server

OPEN_JDK_NAME = "openjdk-%d-jdk"

def check_version( version: str ) -> int:
    """检查最适合MC版本的jdk版本

    参数:
        version: MC版本
    """
    _, vers, _ = version.split(".")
    vers = int(vers)
    if vers < 17: # 1.16-
        return 8 # jdk 8
    elif vers == 17: # 1.17
        return 16 # jdk 16
    else: # 1.18+
        return 17 # jdk 17


