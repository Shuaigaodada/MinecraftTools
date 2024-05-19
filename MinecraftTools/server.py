import re
import os
import sys
import json
import tqdm
import time
import paramiko
import threading
from typing import Tuple, Optional, List, Union, Callable, Any
from log import logger, language
from properties import Properties

Function = Tuple[Callable, Any]
CommandType = Optional[Union[Tuple[Tuple[str, Union[Function, str]]], List[Tuple[str, Union[Function, str]]], Tuple[str, Union[Function, str]]]]
if getattr(sys, "frozen", False):
    BASEPATH = sys._MEIPASS
else:
    BASEPATH = os.path.dirname(os.path.abspath(__file__))

class Server:
    __instance: Optional["Server"] = None
    def __new__( cls, hosts: Optional[str] = None, port: Optional[int] = None, key: Optional[str] = None ) -> "Server":
        if cls.__instance == None:
            if hosts == None or port == None:
                raise AttributeError( "启动单例时必须要填入所有参数" )
            cls.__instance = super(Server, cls).__new__( cls )
            cls.__instance.init( hosts, port, key )
            cls.__instance.__create_ssh_channel( )
        return cls.__instance
    
    def __create_ssh_channel( self ) -> None:
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    @staticmethod
    def create_file():
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
    
    def init( self, hosts: str, port: int, key: str ) -> None:
        self.hosts = hosts
        self.port = port
        self.key_file = key
        self.basepath = r"C:\Users\Administrator"
        self.MC_PATH: str = None
        self.JAVA_PATH: str = None
        self.__progress_bar: tqdm.tqdm = None
        self.__last_transferred = 0
        self.properties = Properties()

        
        self.FORGE_VERSION: str = None
        self.JDK_VERSION: str = None
        self.MC_VERSION: str = None
        
        self.SERVER_NAME: str = None
        
        self.__username: str = None
        self.__password: str = None
            
    def connect( self, usr_name: str, pw: str, timeout: float=5, retry: int = 3 ) -> None:
        self.__username = usr_name
        self.__password = pw
        while True:
            try:
                self.ssh.connect(
                    self.hosts,
                    self.port,
                    self.__username,
                    self.__password,
                    key_filename=self.key_file,
                    timeout=timeout
                )
            except TimeoutError:
                logger.error(language["timeout_error"].format(retry))
                retry -= 1
                if retry <= 0:
                    logger.error("连接失败")
                    raise TimeoutError("连接失败")
                continue
            break
        
    
    def join( self, *__path: str ) -> str:
        path = self.MC_PATH
        for p in __path:
            path += "\\" + p
        return path
        
    
    def upload( self, local_path: str, remote_path: str = None ) -> None:
        """上传文件"""
        if remote_path is None:
            remote_path = self.basepath
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path, callback=self.__progress)
        self.__progress_bar.close()
        self.__progress_bar = None
        self.__last_transferred = 0
        sftp.close()
        
    def __progress(self, transferred, total):
        if self.__progress_bar is None:
            self.__progress_bar = tqdm.tqdm(total=total, desc="上传中...", unit="B", unit_scale=True, unit_divisor=1024)
        increment = transferred - self.__last_transferred
        self.__progress_bar.update(increment)
        self.__last_transferred = transferred
    
    def download( self, remote_path: str, local_path: str = "." ) -> None:
        """下载文件"""
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path, local_path, callback=self.__progress)
        sftp.close()

    def send( self, cmd: str, output: bool = True, breakout: CommandType = None ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        """发送命令"""
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=output)
        if output:
            while not stdout.channel.exit_status_ready():
                # 只要没结束，就读取输出流
                while stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(4096).decode("utf8")
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    alldata = ansi_escape.sub('', alldata)

                    print(alldata, end="", flush=True)
                    if breakout is not None:
                        # 检查第一个元素是否是指令集
                        if isinstance(breakout[0], (list, tuple)):
                            for b in breakout:
                                if re.search(b[0], alldata):
                                    if isinstance(b[1], tuple):
                                        func = b[1][0]
                                        func(*b[1][1:])
                                    else:
                                        stdin.write(b[1])
                                        stdin.flush()
                                    
                        else:
                            if re.search(breakout[0], alldata):
                                if isinstance(breakout[1], tuple):
                                    func = breakout[1][0]
                                    func(*breakout[1][1:])
                                else:
                                    stdin.write(breakout[1])
                                    stdin.flush()


        return stdin, stdout, stderr

    def exists( self, *__path: Tuple[str] ) -> bool:
        path = self.join(*__path)
        _, stdout, _ = self.send(f"if exist {path} (echo 0) else (echo 1)")
        return stdout.read().decode() == "0"

    def exec( self, cmd: str ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True)
        def __ouput():
            while not stdout.channel.exit_status_ready():
                while stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(4096).decode("utf8")
                    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                    alldata = ansi_escape.sub('', alldata)
                    print(alldata, end="", flush=True)
        threading.Thread(target=__ouput).start()
        return stdin, stdout, stderr
    
    def run( self ) -> None:
        if not self.exists("call-run.bat"):
            with open(os.path.join(BASEPATH, "prefile", "call-run.bat"), "r") as fp:
                cmd = fp.read()
            cmd = cmd.replace("MC_PATH", self.MC_PATH)
            print(cmd)
            with open(os.path.join(BASEPATH, "cache", "call-run.bat"), "w") as fp:
                fp.write(cmd)
            self.upload(os.path.join(BASEPATH, "cache", "call-run.bat"), self.join("call-run.bat"))
        self.send(f"cd /d {self.MC_PATH} && .\call-run.bat")
        
        
    def client_run(self, breakout: CommandType = None) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        logger.info(language["run_server"].format(self.hosts, self.properties.server_port))
        return self.send(f"cd /d {self.MC_PATH} && .\\run.bat", breakout=breakout)
        
    def close(self) -> None:
        Server.__instance = None
        self.ssh.close()
    
    def reconnect(self) -> None:
        self.ssh.close()
        self.__create_ssh_channel()
        self.connect(self.__username, self.__password)
    
    def upload_mods(self) -> None:
        mods = os.listdir(os.path.join(BASEPATH, "mods"))
        for mod in mods:
            self.upload(os.path.join(BASEPATH, "mods", mod), self.join("mods", mod))

    def exec_command( self, cmd: str ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        command = \
            f'start /B cmd /c "{cmd}" > output.txt 2>&1'
        return self.exec(command)

    def check(self) -> bool:
        cmd = f"netstat -ano | findstr :{self.properties.server_port}"
        _, stdout, _ = self.ssh.exec_command(cmd)
        output = stdout.read().decode()
        return str(self.properties.server_port) in output
    
    def kill_server(self) -> None:
        cmd = f"netstat -ano | findstr :{self.properties.server_port}"
        _, stdout, _ = self.ssh.exec_command(cmd)
        output = stdout.read().decode()
        pid = None
        for line in output.splitlines():
            if str(self.properties.server_port) in line:
                pid = line.split()[-1]
                break
        
        if pid is not None:
            logger.info(f"find pid: {pid}")
            cmd = f"taskkill /F /PID {pid}"
            self.ssh.exec_command(cmd)
        return
    