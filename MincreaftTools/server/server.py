import os
import re
import paramiko
from typing import Tuple, Optional

class Server:
    __instance: Optional["Server"] = None
    def __new__( cls, hosts: Optional[str] = None, port: Optional[int] = None, key: Optional[str] = None ) -> "Server":
        if cls.__instance == None:
            if hosts == None or port == None or key == None:
                raise AttributeError( "启动单例时必须要填入所有参数" )
            cls.__instance = super(Server, cls).__new__( cls )
            cls.__instance.init( hosts, port, key )
            cls.__instance.__create_ssh_channel( )
        return cls.__instance
    
    def __create_ssh_channel( self ) -> None:
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def init( self, hosts: str, port: int, key: str ) -> None:
        self.hosts = hosts
        self.port = port
        self.key_file = key
        self.basepath = r"C:\Users\Administrator"
        self.MC_PATH: str = None
        self.JAVA_PATH: str = None
    
    def connect( self, usr_name: str, pw: str ) -> None:
        self.ssh.connect(
            self.hosts,
            self.port,
            usr_name,
            pw,
            key_filename=self.key_file
        )
    
    def join( self, *__path: str ) -> None:
        path = self.MC_PATH
        for p in __path:
            path += f"\\{p}"
        return path
        
    
    def upload( self, local_path: str, remote_path: str = None ) -> None:
        """上传文件"""
        if remote_path is None:
            remote_path = self.basepath
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path, callback=self.__progress)
        sftp.close()
        print()
        
    def __progress(self, transferred, total):
        print("\rTransferred: {0}\tOut of: {1}".format(transferred, total), end="", flush=True)
    
    def download( self, remote_path: str, local_path: str = "." ) -> None:
        """下载文件"""
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path, local_path, callback=self.__progress)
        sftp.close()

    def send( self, cmd: str, output: bool = True, breakout: re.Match[str] = None ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        """发送命令"""
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=output)
        if output:
            while not stdout.channel.exit_status_ready():
                # 只要没结束，就读取输出流
                while stdout.channel.recv_ready():
                    alldata = stdout.channel.recv(4096).decode("utf8")
                    pattern = r'[^\w\n :,]'
                    alldata = re.sub(pattern, '', alldata)
                    print(alldata, end="", flush=True)
                    if breakout is not None:
                        if isinstance(breakout, (list, tuple)):
                            for b in breakout:
                                if re.search(b, alldata):
                                    stdin.write("\x1a")
                                    stdin.flush()
                        else:
                            if re.search(breakout, alldata):
                                stdin.write("\x1a")
                                stdin.flush()
                            

                
        return stdin, stdout, stderr

    def run(self) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        print("\n运行服务器中...")
        return self.send(f"cd /d {self.MC_PATH} && .\\run.bat", breakout=["Failed to load eula.txt", "You need to agree to the EULA in order", "Press any key to continue"])
        
        
