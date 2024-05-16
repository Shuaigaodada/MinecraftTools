import os
import re
import requests
from fake_headers import Headers
from typing import Optional
from server import Server
from os.path import join, abspath, dirname
import time
from log import logger, language

OPEN_JDK_NAME = "openjdk-%d-jdk"

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
            return 8 # jdk 8
        elif vers == 17: # 1.17
            logger.info(language["jdk_version"].format(version, 16))
            return 16 # jdk 16
        else: # 1.18+
            logger.info(language["jdk_version"].format(version, 17))
            return 17 # jdk 17

    def download() -> str:
        logger.info(language["load_version"])
        version = Java.MC_version(Java().version)
        logger.info(language["load_version_success"].format(version))
        
        url_mapping = {
            8: "https://download.java.net/openjdk/jdk8u43/ri/openjdk-8u43-windows-i586.zip",
            16: "https://download.java.net/openjdk/jdk16/ri/openjdk-16+36_windows-x64_bin.zip",
            17: "https://download.java.net/openjdk/jdk17/ri/openjdk-17+35_windows-x64_bin.zip"
        }
        
        logger.info(language["generate_headers"])
        headers = Headers("chrome", "win", True).generate()
        logger.info(language["generate_headers_success"].format(headers))
        logger.info(language["requesting"].format(url_mapping[version]))
        respones = requests.get( url_mapping[version], headers=headers)
        logger.info(language["request_success"].format(url_mapping[version]))        
        if respones.status_code != 200:
            logger.info(language["request_fail"].format(respones.status_code))
            return Java.download( version, path )
        
        logger.info(language["request_success"].format(url_mapping[version]))
        
        path = abspath(join(".", f"windows-java{version}.zip"))
        
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
                dirname(abspath(__file__)),
                "tools",
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
        
    

        
