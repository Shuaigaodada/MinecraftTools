from java import Java
from forge import Forge
from server import Server
import os
from loguru import logger

MC_VERSION = ""
SERVER_IP = ""
PORT = 22
USER = None
PASSWORD = None
KEY = None

def create_server():
    logger.info("连接中...")
    Server(
        SERVER_IP,
        PORT,
        key=KEY
    ).connect(USER, PASSWORD)
    logger.info("连接成功")
    
    latest, recommended = \
    Forge.version(MC_VERSION)
    forge_pack = Forge.download(recommended)
    java_pack = Java.download()

    Java.send(java_pack)
    Forge.install(forge_pack)

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
    


