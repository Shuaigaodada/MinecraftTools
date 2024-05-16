import os
import sys
import time
import requests
import configparser
import re as regex
from typing import *
from os.path import join, dirname, abspath
from server import Server
from bs4 import BeautifulSoup
from fake_headers import Headers
from log import logger, language

if getattr(sys, "frozen", False):
    BASEPATH = sys._MEIPASS
else:
    BASEPATH = dirname(abspath(__file__))
SAVE_PATH_CONFIG_PATH = join(os.path.dirname(os.path.abspath(__file__)), "config", "save_path.cfg")

class Forge:
    @staticmethod
    def version(version: str) -> Tuple[str, str]:
        logger.info(language["load_version"])
        server: Server = Server()
        if server.MC_PATH is None:
            server.MC_VERSION = version
            server.MC_PATH = server.basepath + "\\" + f"forge_{version}_server"
        
        logger.info(language["generate_headers"])
        headers = Headers("chrome", "win", True).generate()
        logger.info(language["generate_headers_success"].format(headers))
        url = "https://files.minecraftforge.net/net/minecraftforge/forge/index_{}.html".format(version)
        logger.info(language["requesting"].format(url))
        respone = requests.get( url, headers=headers )
        logger.info(language["request_success"].format(url))
        logger.info(language["encoding"])
        respone.encoding = "utf-8"
        logger.info(language["encode_success"].format(respone.encoding))
        if respone.status_code != 200:
            raise RuntimeError(language["request_fail"].format(respone.status_code))

        logger.info(language["parse"])
        html = respone.text
        soup = BeautifulSoup( html, "lxml" )
        vers = soup.find_all( "small" )
        
        if not vers:
            logger.warning(language["load_version_fail"])
            return Forge.version( version )
        logger.info(language["parse_success"])
        logger.info(str(vers))

        logger.info(language["filter"])
        vers_pattern = regex.compile(r"\d+\.\d+\.\d+ - (\d+\.\d+\.\d+(\.\d+)?)")

        v: List[str] = []
        for ver in vers:
            match = vers_pattern.search( ver.text )
            if match:
                v.append(match.group(1))
        
        latest, recommended = v 
        logger.info(language["filter_success"])
        logger.info(language["latest"].format(latest))
        logger.info(language["recommended"].format(recommended))
        return latest, recommended

    @staticmethod
    def download( forge_ver: str ) -> str:
        Server().FORGE_VERSION = forge_ver
        mc_ver = Server().MC_VERSION
        Server().MC_VERSION = mc_ver
        url = \
f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_ver}-{forge_ver}/forge-{mc_ver}-{forge_ver}-installer.jar"
        logger.info(language["generate_headers"])
        headers = Headers("chrome", "win", True).generate()
        logger.info(language["generate_headers_success"].format(headers))
        logger.info(language["requesting"].format(url))
        respones = requests.get(url, headers=headers)
        logger.info(language["request_success"].format(url))
        
        config = configparser.ConfigParser()
        config.read( SAVE_PATH_CONFIG_PATH )
        path = join(
            config.get("PATHS", "forge_path"),
            f"forge-{mc_ver}-{forge_ver}-installer.jar"
        )
        
        logger.info(language["writing"])
        with open( path, "wb" ) as fp:
            fp.write(respones.content)
        logger.info(language["write_success"])
        return path

    @staticmethod
    def install( forge_path: str ) -> None:
        server = Server()
        logger.info(language["uploading"].format("Forge"))
        server.upload( forge_path, server.join( os.path.basename(forge_path)) )
        logger.info(language["upload_success"].format("Forge"))
        
        JAVA_PATH = f"{server.JAVA_PATH}\\bin\\java.exe"
        FORGE_PATH = server.MC_PATH + '\\' + os.path.basename(forge_path)
        logger.info(language["set_PATH"].format("JAVA_PATH"))
        logger.info(language["install_forge"].format(FORGE_PATH))
        command = \
            f"cmd /c \"cd /d {server.MC_PATH} && \"{JAVA_PATH}\" -jar \"{FORGE_PATH}\" -installServer\""
        print(command)
        for i in range(10):
            logger.info(language["waiting_buff_java"].format(10 - i))
            time.sleep(1)
        server.send( command )
        print()
        for i in range(10):
            logger.info(language["waiting_buff_forge"].format(10 - i))
            time.sleep(1)
        logger.info(language["send_success"].format(command))
        
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        run_name = "run.bat" if int(server.MC_VERSION.split(".")[1]) >= 13 else "1.13-run.bat"
        
        with open( os.path.join(base_path, "prefile", run_name), "r" ) as fp:
            cmds = fp.read()
            
        SERVER_FORGE_PATH = server.MC_PATH + f"\\forge-{Server().MC_VERSION}-{Server().FORGE_VERSION}.jar"
        print(cmds)

        new_run_bat = os.path.join(base_path, "cache", "run.bat")
        cmds = cmds.replace("JAVA_PATH", JAVA_PATH).replace("MC_PATH", server.MC_PATH).replace("FORGE_PATH", SERVER_FORGE_PATH)
        with open(new_run_bat, "w") as fp:
            fp.write(cmds)
            
        logger.info(language["replace_run_bat"].format( os.path.join(base_path, "prefile", run_name) ))
        server.upload( new_run_bat, server.join("run.bat") )
        server.run(breakout=("You need to agree to the EULA in order", "Y\n")) # first run, create all file

        
        # upload eula.txt
        eula_path = base_path + "/prefile/eula.txt"
        logger.info(language["uploading"].format("eula.txt"))
        server.upload( eula_path, server.join("eula.txt") )
        logger.info(language["upload_success"].format("eula.txt"))
        server.run(breakout=(("Successfully init", (server.reconnect, )), ("Done", (server.reconnect, ))))
        logger.info(language["install_success"].format("Forge"))

