from java import Java
from forge import Forge
from server import Server
import os
from loguru import logger
import configparser

MC_VERSION = ""
SERVER_IP = ""
PORT = 22
USER = None
PASSWORD = None
KEY = None
BASEPATH = r"C:\Users\Administrator"
NAME = None


def create_server():
    Server.create_file()
    logger.info("连接中...")
    server = Server(
        SERVER_IP,
        PORT,
        key=KEY
    )
    server.connect(USER, PASSWORD)
    server.SERVER_NAME = NAME
    logger.info("连接成功")
    
    try:
        latest, recommended = \
        Forge.version(MC_VERSION)
        forge_pack = Forge.download(recommended)
        java_pack = Java.download()

        Java.send(java_pack)
        Forge.install(forge_pack)
    finally:
        server.close()

def set_properties():
    server = Server()
    basefile = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
    
    server_properties = os.path.join(
        basefile, "cache", "server.properties"
    )
    server.upload(server_properties, server.join("server.properties"))
    
def auto_setup_properties():
    pass

def setup_properties():
    pass


def run():
    try:
        server = Server()
    except Exception as e:
        server = Server(
            SERVER_IP,
            PORT,
            key=KEY
        )
        server.connect(USER, PASSWORD)
        Forge.version(MC_VERSION)
    stdin, stdout, stderr = server.exec(f"cd /d {server.MC_PATH} && .\\run.bat")
    # stdin, stdout, stderr = server.exec("dir")
    try:
        while True:
            cmd = input(">>> ")
            if cmd == "exit":
                stdin.close()
                stdout.close()
                stderr.close()
                server.close()
                break
            stdin.write(cmd)
            stdin.flush()
            import time
            time.sleep(1)
            print()
    finally:
        stdin.close()
        stdout.close()
        stderr.close()
        server.close()
        logger.info("已关闭")
