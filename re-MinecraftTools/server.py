import re
import os
import sys
import json
import paramiko
from config import basepath as BASEPATH

from typing import *

# define type
__FunctionType = Tuple[Callable[..., Any], Any]
__TupleType = Tuple[Union[str, Union[__FunctionType, str]]]
__ListType = List[Union[str, Union[__FunctionType, str]]]
CommandType = Optional[Union[__ListType, __TupleType], ]

class Server:
    """服务器类，用于处理服务器相关操作，这是一个单例"""
    __instance: Optional["Server"] = None
    def __new__( cls ):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init( self ) -> None:
        """初始化服务器类"""
        self.minecraft_path: str = None
        self.minecraft_version: str = None
        self.forge_version: str = None
        self.jdk_version: str = None
        
        self.hosts: str = None
        self.port: int = 22
        self.keyfile: str = None

        self.forge_path: str = None
        self.jdk_path: str = None
        
        self.__username: str = None
        self.__password: str = None
        
        self.ssh: paramiko.SSHClient = None
        
        self.__generate_files()
    
    def __generate_files( self ) -> None:
        """生成服务器所需文件"""
        os.makedirs( os.path.join(BASEPATH, "cache"), exist_ok=True )
        os.makedirs( os.path.join(BASEPATH, "config"), exist_ok=True )
        os.makedirs( os.path.join(BASEPATH, "logs"), exist_ok=True )
        os.makedirs( os.path.join(BASEPATH, "mods"), exist_ok=True )
        if not os.path.exists( os.path.join( BASEPATH, "config", "save_path.cfg" ) ):
            with open( os.path.join( BASEPATH, "config", "save_path.cfg" ), "w" ) as f:
                f.write("[PATHS]\n")
                f.write(f"java_path = {os.path.join(BASEPATH, 'cache')}\n")
                f.write(f"forge_path = {os.path.join(BASEPATH, 'cache')}")
        if not os.path.exists( os.path.join( BASEPATH, "config", "server.cfg" ) ):
            with open( os.path.join( BASEPATH, "config", "server.cfg" ), "w" ) as f:
                f.write("[Server]\n")
                f.write("hosts = \n")
                f.write("port = 22\n")
                f.write("user = Administrator\n")
                f.write("password = \n")
                f.write("key = \n")
                f.write("[MC]\n")
                f.write("version = \n")
                f.write("[Forge]\n")
                f.write("version = \n")
        if not os.path.exists( os.path.join( BASEPATH, "config", "url.json" ) ):
            url_json = {
                    "java8": {
                        "url": "https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u412-b08/openlogic-openjdk-8u412-b08-windows-x64.zip",
                        "name": "openlogic-openjdk-8u412-b08-windows-64"
                    },
                    "java16": {
                        "url": "https://download.java.net/openjdk/jdk16/ri/openjdk-16+36_windows-x64_bin.zip",
                        "name": "jdk-16"
                    },
                    "java17": {
                        "url": "https://download.java.net/openjdk/jdk17/ri/openjdk-17+35_windows-x64_bin.zip",
                        "name": "jdk-17"
                    }
                }
            with open( os.path.join( BASEPATH, "config", "url.json" ), "w" ) as f:
                f.write(json.dumps(url_json))
                
    def __join( self, *__path: Tuple[str] ) -> str:
        """连接路径"""
        path: str = os.path.join(self.minecraft_path, *__path)
        return path.replace("/", "\\")
    
    def __create_channel( self ) -> None:
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
    
    def set_hosts( self, hosts: str, keyfile: str = None, /, port: int = 22 ) -> None:
        """设置服务器地址"""
        self.hosts = hosts
        self.port = port
        self.keyfile = keyfile
    
    def connect( self, usrname: str, password: str, /, timeout: float = 10 ) -> None:
        """连接服务器
        
        抛出：
            TimeoutError: 连接超时"""
        self.__create_channel()
        self.__username = usrname
        self.__password = password
        
        self.ssh.connect(
            self.hosts,
            self.port,
            self.__username,
            self.__password,
            key_filename=self.keyfile,
            timeout=timeout
        )

    def upload( self, local: str, remote: str, callback: Callable = None ) -> None:
        remote = self.__join(remote)
        sftp = self.ssh.open_sftp()
        sftp.put(local, remote, callback=callback)
        sftp.close()
        
    def download( self, remote: str, local: str, callback: Callable = None ) -> None:
        remote = self.__join(remote)
        sftp = self.ssh.open_sftp()
        sftp.get(remote, local, callback=callback)
        sftp.close()
        
        
    def close( self ) -> None:
        """关闭连接"""
        self.ssh.close()
        
        
    
    