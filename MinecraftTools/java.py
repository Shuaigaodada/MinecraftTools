import os
import re
import sys
import json
import requests
import configparser
from fake_headers import Headers
from server import Server
from os.path import join, abspath, dirname
from log import logger, language

if getattr(sys, "frozen", False):
    BASEPATH = sys._MEIPASS
else:
    BASEPATH = dirname(abspath(__file__))

OPEN_JDK_NAME = "openjdk-%d-jdk"
URL_CONFIG_PATH = join(BASEPATH, "config", "url.json")
SAVE_PATH_CONFIG_PATH = join(BASEPATH, "config", "save_path.cfg")

class Java:
    @property
    def version( self ) -> str:
        return Server().MC_PATH.split('_')[1]
    
    @staticmethod
    def MC_version( version: str ) -> int:
        """检查最适合MC版本的jdk版本

        参数:
            version: MC版本
        """
        vers = int(version.split(".")[1])
        if vers < 17: # 1.16-
            logger.info(language["jdk_version"].format(version, 8))
            Server().JDK_VERSION = "8"
            return 8 # jdk 8
        elif vers == 17: # 1.17
            logger.info(language["jdk_version"].format(version, 16))
            Server().JDK_VERSION = "16"
            return 16 # jdk 16
        else: # 1.18+
            logger.info(language["jdk_version"].format(version, 17))
            Server().JDK_VERSION = "17"
            return 17 # jdk 17

    def download() -> str:
        logger.info(language["load_version"])
        version = Java.MC_version( Server().MC_VERSION )
        logger.info(language["load_version_success"].format(version))
        
        logger.info(language["load_url"])
        with open(URL_CONFIG_PATH, "r") as fp:
            url_mapping = json.load( fp )
        logger.info(language["load_url_success"])
        
        mapping_version = "java" + str(version)
        
        logger.info(language["generate_headers"])
        headers = Headers("chrome", "win", True).generate()
        logger.info(language["generate_headers_success"].format(headers))
        logger.info(language["requesting"].format(url_mapping[mapping_version]["url"]))
        respones = requests.get( url_mapping[mapping_version]["url"], headers=headers)
        logger.info(language["request_success"].format(url_mapping[mapping_version]["url"]))        
        if respones.status_code != 200:
            logger.info(language["request_fail"].format(respones.status_code))
            return Java.download( version, path )
        
        logger.info(language["request_success"].format(url_mapping[mapping_version]["url"]))
        
        logger.info(language["load_config"].format(SAVE_PATH_CONFIG_PATH))
        config = configparser.ConfigParser()
        config.read( SAVE_PATH_CONFIG_PATH )
        logger.info(language["load_config_success"].format(SAVE_PATH_CONFIG_PATH))
        
        path = join(config.get("PATHS", "java_path"), f"windows-java{version}.zip")
        
        logger.info(language["writing"])
        with open( path, "wb" ) as fp:
            fp.write( respones.content )
        logger.info(language["write_success"])
        logger.info(language["download_success"].format("Java"))
        
        return path

    def send( pack: str ) -> None:
        logger.info(language["generate_dir"])
        server = Server()
        
        basename = os.path.basename( pack )
        java_path = server.join( basename )
        unzip_path = server.join( "unzip.exe" )
        
        
        server.send(f"mkdir {server.MC_PATH}", output=False)
        
        logger.info(language["generate_dir_success"])
        logger.info(language["uploading"].format("Java zip"))
        server.upload( pack, java_path )
        logger.info(language["upload_success"].format("Java zip"))
        
        logger.info(language["uploading"].format("unzip.exe"))
        server.upload(
            join(
                BASEPATH,
                "prefile",
                "unzip.exe"
            ),
            unzip_path
        )
        logger.info(language["upload_success"].format("unzip.exe"))
        logger.info(language["unziping"])
        _, stdout, _ = server.send(f"{unzip_path} {java_path}", output=False)
        while stdout.channel.exit_status_ready(): pass
            
        logger.info(language["unzip_success"])
        
        
        match = re.search(r"java(\d+)", pack)
        if not match:
            raise ValueError("Java version not found in the path")
        
        __ver = int(match.group(1))
        server.JAVA_PATH = server.join( f"java{__ver}" )
        
    

        
