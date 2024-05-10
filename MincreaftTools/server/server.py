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
    
    def connect( self, usr_name: str, pw: str ) -> None:
        self.ssh.connect(
            self.hosts,
            self.port,
            usr_name,
            pw,
            key_filename=self.key_file
        )
        
    def upload( self, local_path: str, remote_path: str = "." ) -> None:
        """上传文件"""
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    
    def download( self, remote_path: str, local_path: str = "." ) -> None:
        """下载文件"""
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def send( self, cmd: str ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        """发送命令"""
        return self.ssh.exec_command( cmd )
        
